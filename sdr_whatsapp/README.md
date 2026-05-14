# SDR WhatsApp Agent

**Stack:** Anthropic API (Claude Haiku 4.5 + Sonnet 4.6) + Evolution API + FastAPI
**Sem n8n. Sem Redis pra histórico. Sem agent loop manual.**

Implementação alternativa ao [`workers/agents/`](../workers/agents/) (LangChain), focada em **otimização agressiva de custo** via 3 camadas: model router, context compaction e prompt caching.

---

## Arquitetura de Custo (3 camadas)

```
Mensagem do Lead
      │
      ▼
┌─────────────────────────────────────────────────┐
│  CAMADA 1: MODEL ROUTER (Haiku 4.5 — $1/MTok)  │
│  Classifica intenção em ~50 tokens              │
│  Decide qual modelo responde                    │
└─────────────────────────────────────────────────┘
      │ category → model_to_use
      ▼
┌─────────────────────────────────────────────────┐
│  CAMADA 2: CONTEXT COMPACTOR                    │
│  Monitora uso da context window                 │
│  Compacta quando atingir 40% (80k tokens)       │
│  Resumo feito pelo Haiku (barato)               │
└─────────────────────────────────────────────────┘
      │ histórico enxuto
      ▼
┌─────────────────────────────────────────────────┐
│  CAMADA 3: SDR AGENT (Sonnet 4.6 — $3/MTok)    │
│  System prompt cacheado (TTL 1h)                │
│  Tool use: send_whatsapp, CRM, Calendly         │
│  -90% no custo de input após 1º turn            │
└─────────────────────────────────────────────────┘
```

---

## Economia Real por Turn

| Componente         | Sem otimização | Com otimização |
|--------------------|----------------|----------------|
| System prompt (2k tokens) | $0.006/turn | **$0.0006/turn** (cache hit) |
| Classificação      | Sonnet $0.009 | **Haiku $0.003** |
| Contexto crescente | Sem compaction → até $0.15/turn | **Compacta → ~$0.02/turn** |
| **Turn típico**    | ~$0.030       | **~$0.008** |

**Economia estimada: ~73% vs sem otimização.**

### 100 leads/dia, 8 turns médios

| Cenário | Custo/dia | Custo/mês |
|---------|-----------|-----------|
| Sem otimização | ~$24/dia | ~$720/mês |
| Com as 3 otimizações | ~$6.50/dia | **~$195/mês** |

---

## Estrutura

```
sdr_whatsapp/
├── sdr_config.py         # Configurações centrais, modelos, preços
├── model_router.py       # Classifica mensagem com Haiku antes do Sonnet
├── context_compactor.py  # Enxuga histórico ao atingir 40% da context window
├── sdr_agent.py          # Agente principal com caching + tool use
├── webhook_server.py     # FastAPI: recebe Evolution API, orquestra tudo
└── integrations/         # 🔌 Clientes async para APIs externas
    ├── evolution.py      # Evolution API (envio WhatsApp + typing + read)
    ├── crm.py            # HubSpot + Pipedrive (upsert lead, BANT, stage)
    ├── calendly.py       # Single-use scheduling links
    └── slack.py          # Notificação de handoff via Block Kit
```

## Integrações implementadas

Todas as 5 tools do agent (`send_whatsapp_message`, `get_lead_context`,
`book_meeting`, `update_crm`, `handoff_to_human`) estão conectadas a APIs reais:

### 📱 Evolution API ([evolution.py](integrations/evolution.py))
- `send_text(phone, message)` — POST `/message/sendText/{instance}`
- `send_typing_indicator(phone)` — UX humano (mostra "digitando...")
- `mark_as_read(message_id, phone)` — duplo check azul

### 📊 CRM ([crm.py](integrations/crm.py))
- **HubSpot** (default): Contacts API v3 com campos custom `bant_score`, `sdr_stage`, `sdr_notes`
- **Pipedrive**: Persons API com Notes vinculadas
- Selecionável via `CRM_PROVIDER=hubspot|pipedrive`
- `get_lead_by_phone(phone)` retorna `{name, email, company, bant_score, stage, notes}`
- `upsert_lead(phone, stage, bant_score, notes)` cria/atualiza

### 📅 Calendly ([calendly.py](integrations/calendly.py))
- `create_single_use_link()` — cria link de uso único (após o lead agendar, expira)
- Fallback gracioso para link público se a API falhar
- Atualiza CRM e envia link via WhatsApp automaticamente

### 💬 Slack ([slack.py](integrations/slack.py))
- `send_handoff()` notifica via Block Kit rico:
  - Header com emoji de prioridade (🟡🟠🔴)
  - Campos: nome, telefone, empresa, BANT score
  - Resumo da conversa
  - Botão direto pra abrir WhatsApp Web
- Configurado via `SLACK_WEBHOOK_URL` (Incoming Webhook)

### Fluxo do `book_meeting` (exemplo)
```
1. Sonnet decide chamar book_meeting(phone, lead_name)
2. CalendlyClient cria single-use link
3. CRM marca lead como stage="cta"
4. Evolution envia link no WhatsApp com texto personalizado
5. Retorna meeting_url ao agent que confirma com o lead
```

---

## Deploy

### 1. Instalar dependências
```bash
cd sdr_whatsapp
pip install -r requirements.txt
```

### 2. Variáveis de ambiente
```bash
cp .env.example .env
# edite com sua chave
export $(cat .env | xargs)
```

### 3. Rodar
```bash
uvicorn webhook_server:app --host 0.0.0.0 --port 8000
```

### 4. Configurar webhook na Evolution API
```http
POST https://sua-evolution.api/webhook/set/sua-instancia
{
  "webhook": {
    "url": "https://seu-servidor:8000/webhook/evolution",
    "events": ["messages.upsert"]
  }
}
```

---

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/webhook/evolution` | Recebe eventos da Evolution API |
| `GET` | `/health` | Health check + nº de conversas ativas |
| `GET` | `/cost-report` | Dashboard de custo por lead (ranking) |

---

## Boost vs SDR WhatsApp — qual usar?

| Caractrística | `workers/agents/` (LangChain) | `sdr_whatsapp/` (Anthropic direto) |
|---------------|-------------------------------|-------------------------------------|
| Stack | LangChain + OpenAI/Anthropic | Anthropic SDK puro |
| WhatsApp gateway | Meta Cloud API | Evolution API (Baileys) |
| Roteamento de modelo | Único modelo | Haiku classifica + Sonnet responde |
| Cache de prompt | Não | Sim — TTL 1h, -90% input |
| Compaction de contexto | Não | Sim — auto aos 40% da janela |
| Histórico | Redis | In-memory (dict) — substituir por Redis |
| Custo típico/turn | ~$0.005 (gpt-4o-mini) | ~$0.008 (Sonnet 4.6 c/ cache) |
| Vantagem | Plug com Meta oficial + LangChain ecosystem | Custo ultra-otimizado para volume |

**Use `sdr_whatsapp/`** quando:
- Volume alto (>1k mensagens/dia)
- Quer Anthropic stack pura
- Já tem ou prefere Evolution API
- Precisa de controle granular sobre custo

**Use `workers/agents/`** quando:
- Precisa de WhatsApp Cloud API oficial Meta
- Quer compatibilidade com LangChain (LangSmith, etc.)
- Multi-LLM provider (OpenAI, Anthropic, Google)

---

## Próximos passos sugeridos

- [x] ~~Implementar `execute_tool()` com chamadas reais à Evolution API e CRM~~ ✅
- [ ] Substituir `conversation_store` dict por Redis (persistência entre restarts)
- [ ] Adicionar autenticação no webhook (validar secret da Evolution API)
- [ ] Dashboard de custo via `/cost-report` endpoint (Grafana/Metabase)
- [ ] Testes E2E com mocks das 4 integrações
- [ ] Rate limiter por número de telefone (evitar spam)
- [ ] Suporte a mensagens de mídia (áudio → STT, imagem → vision)
- [ ] Mover para Managed Agents API quando precisar de sessões longas (>1h)

---

## Por que NÃO usar Managed Agents ainda?

O Managed Agents é ideal para **tarefas longas e assíncronas** (minutos/horas).
O SDR via WhatsApp é **request/response** — cada mensagem é um turn rápido.
A abordagem Messages API direta é mais simples, mais barata e suficiente.

Migre para Managed Agents se precisar de: execução >5 min, filesystem persistente, ou orquestração multi-agente com subagents.
