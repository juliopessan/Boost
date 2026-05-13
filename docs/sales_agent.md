# Sales Agent — Documentação

Agente de vendas WhatsApp construído sobre LangChain, integrado ao roteador de mensagens do Boost.

## Arquitetura

```
Mensagem WhatsApp
       │
       ▼
┌──────────────────┐
│  AISalesHandler  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐    Se human_request/complaint
│ IntentClassifier │ ──────────────► transferir_humano
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   SalesAgent     │ ←─── Redis (histórico + estágio do funil)
│  (LangChain      │
│   AgentExecutor) │
└────────┬─────────┘
         │
         ▼
   Tools chamadas conforme necessidade:
   • consultar_catalogo
   • verificar_estoque
   • calcular_frete
   • buscar_cliente / registrar_lead
   • criar_oportunidade
   • transferir_humano
   • agendar_followup
```

## Estágios do Funil

| Estágio | O que o agente faz | Tools típicas |
|---------|-------------------|---------------|
| `greeting` | Cumprimenta, identifica-se, primeira pergunta aberta | `buscar_cliente` |
| `qualification` | BANT adaptado (Need → Urgency → Volume → Decisor) | `registrar_lead` |
| `pitch` | Recomenda 1-2 produtos baseado em qualificação | `consultar_catalogo` |
| `objection` | Trata objeções com Senti-Sentiu-Descobriu | `verificar_estoque` |
| `closing` | Fechamento por escolha alternativa | `criar_oportunidade` |
| `checkout` | Coleta CPF, endereço, forma de pagamento | `calcular_frete` |
| `post_sale` | Confirma pedido, define expectativa, abre canal | — |
| `human_handoff` | Transferiu para atendente | `transferir_humano` |

## Prompt Templates Disponíveis

Todos em [workers/agents/prompts/](../workers/agents/prompts/):

| Arquivo | Templates |
|---------|-----------|
| `system_persona.py` | `SALES_AGENT_SYSTEM_PROMPT`, `GREETING_PROMPT` |
| `qualification.py` | `QUALIFICATION_PROMPT`, `QUALIFICATION_QUESTIONS` |
| `pitch.py` | `PRODUCT_PITCH_PROMPT`, `OBJECTION_HANDLING_PROMPT`, `CLOSING_PROMPT` |
| `checkout.py` | `CHECKOUT_PROMPT`, `ORDER_CONFIRMATION_PROMPT`, `POST_SALE_PROMPT` |
| `classifier.py` | `INTENT_CLASSIFIER_PROMPT`, `HUMAN_HANDOFF_PROMPT` |

## Customizando para sua marca

Edite as variáveis no `.env`:

```bash
COMPANY_NAME=SuaEmpresa
PRODUCT_CATEGORY=cosméticos
```

Para personalizações mais profundas, edite `SALES_AGENT_SYSTEM_PROMPT` em `system_persona.py` — esse é o "DNA" da agente Júlia.

## Trocar de modelo

No `SalesAgent.__init__` ou `IntentClassifier.__init__`:

```python
agent = SalesAgent(model="gpt-4o")          # mais caro, mais inteligente
agent = SalesAgent(model="gpt-4o-mini")     # default, ótimo custo/qualidade
```

Para usar Claude via Anthropic SDK, troque `ChatOpenAI` por `ChatAnthropic` em `chains/sales_agent.py`.

## Custos estimados

| Modelo | Por conversa (10 turnos) | 10k conversas/mês |
|--------|--------------------------|-------------------|
| gpt-4o-mini | ~$0.005 | ~$50 |
| gpt-4o | ~$0.08 | ~$800 |
| claude-haiku-4 | ~$0.003 | ~$30 |
| claude-sonnet-4 | ~$0.05 | ~$500 |

Recomendação MVP: `gpt-4o-mini` para o agent + `gpt-4o-mini` para classifier.

## Toggle on/off

Variável `USE_AI_AGENT` no `.env`:
- `true` → usa LangChain `AISalesHandler`
- `false` → usa o `TextHandler` estático (menu numérico fallback)

Útil para A/B test ou rollback rápido em caso de problema com o LLM.

## Segurança e Guardrails

O `SALES_AGENT_SYSTEM_PROMPT` define regras duras:

1. Nunca inventar preços/prazos → sempre usar tools
2. Nunca prometer desconto não autorizado
3. Transferir humano em: pedido de humano, abuso, reclamação, suporte a pedido existente
4. Resposta sempre curta (formato WhatsApp)

Para guardrails adicionais, considere:
- [Guardrails AI](https://github.com/guardrails-ai/guardrails) para validação de output
- Moderação OpenAI para detectar conteúdo ofensivo
- Rate limiting no webhook por phone_hash
