# ⚡ Boost

> Plataforma de orquestração de mensagens WhatsApp com **agente de vendas IA** — substitui o n8n com stack própria AWS (FastAPI + SQS + Lambda + Redis) e LangChain.

[![Stack](https://img.shields.io/badge/stack-AWS%20%2B%20LangChain-blue)](https://github.com/juliopessan/Boost)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-yellow)](https://www.python.org)
[![React](https://img.shields.io/badge/react-18-61dafb)](https://react.dev)

---

## ✨ Por que Boost?

- **Zero licença** — sem fair-code, sem teto de execuções, código 100% seu
- **Agente IA pronto** — 12 prompt templates de vendas + 8 tools LangChain integráveis
- **Stack AWS nativa** — escala linear, custo previsível (~$35/mês para 50k msg)
- **Dashboard em tempo real** — métricas, DLQ, gestão de flows
- **Plug-and-play** — `docker compose up` e está rodando localmente

---

## 🏗️ Arquitetura

```
                    WhatsApp Cloud API
                            │
                            ▼
                  ┌──────────────────┐
                  │  Webhook (ECS)   │  ◄── HMAC-SHA256 validation
                  │    FastAPI       │
                  └─────────┬────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │   SQS FIFO       │  ◄── DLQ após 3 retries
                  │ (boost-messages) │
                  └─────────┬────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ Lambda Router    │
                  └─────────┬────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
       AISalesHandler  ButtonHandler  AudioHandler
              │             │             │
              ▼             ▼             ▼
       ┌─────────────────────────────────────┐
       │  IntentClassifier → SalesAgent       │
       │  (LangChain + OpenAI/Claude)         │
       │                                      │
       │  Tools: catálogo · estoque · frete   │
       │         CRM · handoff · followup     │
       └────────────────┬────────────────────┘
                        │
            ┌───────────┼───────────┐
            ▼           ▼           ▼
       ┌─────────┐ ┌──────────┐ ┌──────────┐
       │ Redis   │ │ Postgres │ │  Supabase │
       │sessions │ │ messages │ │ dashboard │
       └─────────┘ └──────────┘ └──────────┘
```

---

## 📁 Estrutura

```
boost/
├── webhook/              # FastAPI — recebe e valida webhooks WhatsApp
│   ├── main.py
│   ├── routers/          # /webhook (GET verify, POST receive)
│   ├── services/         # SQS publisher, HMAC validator
│   └── models/           # Pydantic schemas
│
├── workers/              # Lambda — roteamento + handlers
│   ├── message_router.py # Entry point Lambda
│   ├── handlers/         # text, button, audio, fallback, AI sales
│   ├── services/         # Redis session, WhatsApp sender, DB
│   └── agents/           # 🧠 LangChain Sales Agent
│       ├── prompts/      # 12 templates por fase do funil
│       ├── tools/        # 8 tools (catálogo, CRM, handoff)
│       ├── chains/       # IntentClassifier, SalesAgent
│       └── configs/      # 🎨 White-label por marca
│           └── keune/    # Lara — agente Keune Brasil
│
├── infra/                # AWS CDK — IaC completo
│   └── stacks/           # queue, storage, webhook, worker
│
├── dashboard/            # React + Tailwind + Supabase
│   └── src/
│       ├── pages/        # Dashboard, Flows, Messages, DLQ, Settings
│       └── components/   # MetricCard, MessageFeed, HourlyChart, etc
│
├── docs/                 # Schema SQL, docs do sales agent
└── scripts/              # LocalStack init, utilitários
```

---

## 🚀 Quick Start (local)

### Pré-requisitos
- Docker + Docker Compose
- Node 18+ (para o dashboard)
- Conta WhatsApp Business API (Meta) com app aprovado
- (Opcional) Chave OpenAI para o sales agent

### Setup em 3 passos

```bash
# 1. Clonar e configurar
git clone https://github.com/juliopessan/Boost.git
cd Boost
cp .env.example .env
# Edite .env com suas credenciais WhatsApp + OPENAI_API_KEY

# 2. Subir a stack local (LocalStack SQS + Redis + Postgres + Webhook)
docker compose up -d

# 3. Rodar o dashboard
cd dashboard
cp .env.example .env.local  # configurar Supabase URL + anon key
npm install
npm run dev                  # http://localhost:5173
```

### Expor o webhook para o Meta

Use ngrok ou Cloudflare Tunnel:

```bash
ngrok http 8000
# Cole a URL HTTPS no Meta Developer Console como Callback URL
# Verify token: o mesmo do WHATSAPP_VERIFY_TOKEN no .env
```

---

## ☁️ Deploy AWS

```bash
cd infra
pip install -r requirements.txt

# Bootstrap uma única vez por conta/região
cdk bootstrap aws://ACCOUNT_ID/us-east-1

# Deploy completo (VPC, SQS, RDS, Redis, ECS, Lambda)
cdk deploy --all

# Outputs incluem o ALB DNS — configure no Meta como webhook URL
```

---

## 🧠 Sales Agent (LangChain)

Agente conversacional de vendas WhatsApp pronto para usar.

### Como ativa

No `.env`:
```bash
USE_AI_AGENT=true
OPENAI_API_KEY=sk-...
COMPANY_NAME=SuaEmpresa
PRODUCT_CATEGORY=cosméticos
```

### Estágios do funil

| Estágio | O que faz | Templates |
|---------|-----------|-----------|
| `greeting` | Cumprimenta, identifica-se, pergunta aberta | `GREETING_PROMPT` |
| `qualification` | BANT WhatsApp (Need→Urgency→Volume→Decisor) | `QUALIFICATION_PROMPT` |
| `pitch` | Recomenda 1-2 produtos do catálogo | `PRODUCT_PITCH_PROMPT` |
| `objection` | Senti-Sentiu-Descobriu por tipo de objeção | `OBJECTION_HANDLING_PROMPT` |
| `closing` | Fechamento por escolha alternativa | `CLOSING_PROMPT` |
| `checkout` | Coleta validada de CPF/CEP/endereço | `CHECKOUT_PROMPT` |
| `post_sale` | Confirma pedido, NPS suave | `POST_SALE_PROMPT` |
| `human_handoff` | Transfere para atendente | `HUMAN_HANDOFF_PROMPT` |

### Tools disponíveis

- **Catálogo**: `consultar_catalogo`, `verificar_estoque`, `calcular_frete`
- **CRM**: `buscar_cliente`, `registrar_lead`, `criar_oportunidade`
- **Atendimento**: `transferir_humano`, `agendar_followup`

Cada tool tem stub funcional pronto — substitua os `# TODO` por integrações reais (HubSpot, Pipedrive, ViaCEP, etc).

### 🎨 White-label por marca

O agente suporta múltiplas marcas via `AGENT_BRAND` no `.env`. Cada marca tem persona, catálogo, FAQ e tools próprias em `workers/agents/configs/<brand>/`.

| Marca | Status | Doc |
|-------|--------|-----|
| `default` | ✅ Agente genérico (Júlia) | [docs/sales_agent.md](docs/sales_agent.md) |
| `keune` | ✅ Lara — Keune Brasil (haircare premium, B2C+B2B) | [docs/keune_agent.md](docs/keune_agent.md) |

**Exemplo Keune:**
```bash
AGENT_BRAND=keune
```
A Lara identifica se é cabeleireiro (B2B → conecta com representante regional) ou consumidor final (B2C → diagnóstico capilar + kit recomendado das linhas Care/So Pure/Style/Color/Man/Blend).

**Para criar uma marca nova:** copie `workers/agents/configs/keune/` para `workers/agents/configs/<sua_marca>/`, ajuste persona/catalog/tools, e o handler resolve automaticamente.

### Trocar OpenAI por Claude

Em [workers/agents/chains/sales_agent.py](workers/agents/chains/sales_agent.py):

```python
from langchain_anthropic import ChatAnthropic
self.llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0.3)
```

Docs completas: [docs/sales_agent.md](docs/sales_agent.md)

---

## 🖥️ Dashboard (FlowCore)

Painel admin em `dashboard/`:

| Página | O que mostra |
|--------|--------------|
| **Dashboard** | 4 métricas chave + chart horário + feed realtime |
| **Flows** | Lista de automações, toggle ativo/inativo |
| **Mensagens** | Tabela paginada com filtro por status |
| **DLQ** | Mensagens com falha, payload e botão reenfileirar |
| **Settings** | Threshold DLQ, timeout sessão, webhooks de alerta |

Atualização automática a cada 30s + subscrição realtime no Supabase para o feed.

---

## 🔧 Variáveis de Ambiente

### WhatsApp (obrigatórias)
| Variável | Descrição |
|----------|-----------|
| `WHATSAPP_APP_SECRET` | Secret do app Meta para HMAC |
| `WHATSAPP_VERIFY_TOKEN` | Token do challenge GET /webhook |
| `WHATSAPP_PHONE_NUMBER_ID` | ID do número Business |
| `WHATSAPP_ACCESS_TOKEN` | Token Cloud API |

### Infraestrutura
| Variável | Descrição |
|----------|-----------|
| `SQS_QUEUE_URL` | URL da fila SQS FIFO |
| `REDIS_URL` | `redis://host:6379` |
| `DATABASE_URL` | DSN PostgreSQL |
| `AWS_REGION` | Default `us-east-1` |

### Sales Agent (opcionais)
| Variável | Descrição | Default |
|----------|-----------|---------|
| `USE_AI_AGENT` | Liga/desliga LangChain | `true` |
| `OPENAI_API_KEY` | Chave OpenAI | — |
| `AGENT_BRAND` | Persona white-label: `default` ou `keune` | `default` |
| `COMPANY_NAME` | Nome da empresa no system prompt (`default` apenas) | `Boost` |
| `PRODUCT_CATEGORY` | Categoria de produto (`default` apenas) | `produtos` |

---

## 💰 Custo estimado

### Infra AWS (50k mensagens/mês)

| Serviço | Custo/mês |
|---------|-----------|
| Lambda | ~$0 (free tier) |
| SQS FIFO | ~$0.02 |
| ElastiCache t3.micro | ~$12 |
| RDS PostgreSQL t3.micro | ~$15 |
| ECS Fargate (0.25 vCPU) | ~$8 |
| **Subtotal infra** | **~$35** |

### Sales Agent (LLM)

| Modelo | Por conversa (~10 turnos) | 10k conversas/mês |
|--------|---------------------------|-------------------|
| `gpt-4o-mini` | ~$0.005 | ~$50 |
| `gpt-4o` | ~$0.08 | ~$800 |
| `claude-haiku-4` | ~$0.003 | ~$30 |
| `claude-sonnet-4` | ~$0.05 | ~$500 |

**Recomendação MVP:** `gpt-4o-mini` ou `claude-haiku-4-5` → total ~$65/mês com 50k msg e agente IA.

---

## 🛣️ Roadmap

- [x] Webhook handler + SQS publisher
- [x] Workers Lambda com handlers por tipo
- [x] Sales Agent LangChain (prompts + tools + chains)
- [x] Dashboard React em tempo real
- [x] Infraestrutura CDK completa
- [x] Configuração white-label por marca (Keune Brasil)
- [ ] Integração real com e-commerce Keune (catálogo via API)
- [ ] Suporte multi-tenant (vários números WhatsApp)
- [ ] Editor visual de flows no dashboard
- [ ] Conector Claude (Anthropic SDK) como alternativa OpenAI
- [ ] Telegram + Instagram (mesmo backend)
- [ ] Marketplace de tools/integrações

---

## 🧪 Testando o webhook localmente

```bash
# Simular evento WhatsApp
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=..." \
  -d @docs/sample_webhook.json
```

Logs do worker:
```bash
docker compose logs -f webhook
```

---

## 📚 Documentação

- [docs/sales_agent.md](docs/sales_agent.md) — Guia completo do agente LangChain (Júlia)
- [docs/keune_agent.md](docs/keune_agent.md) — Configuração Keune Brasil (Lara) com B2C/B2B
- [docs/schema.sql](docs/schema.sql) — Schema PostgreSQL com índices e funções

---

## 🤝 Contribuindo

Issues e PRs são bem-vindos. Para mudanças grandes, abra uma issue primeiro para discutir.

```bash
git clone https://github.com/juliopessan/Boost.git
cd Boost
# faça suas mudanças
git checkout -b feature/minha-feature
git commit -m "feat: descrição"
git push origin feature/minha-feature
# abra PR no GitHub
```

---

## 📄 Licença

MIT © [juliopessan](https://github.com/juliopessan)
