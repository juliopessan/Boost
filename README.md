# Boost

Plataforma de orquestração de mensagens WhatsApp — substitui o n8n com stack própria AWS (FastAPI + SQS + Lambda + Redis).

## Arquitetura

```
WhatsApp API
     │
     ▼
┌─────────────┐     ┌──────────────┐
│   Webhook   │────▶│  SQS FIFO   │
│  (FastAPI)  │     │  + DLQ      │
└─────────────┘     └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │    Lambda    │
                    │  (Router)   │
                    └──────┬───────┘
               ┌───────────┼───────────┐
               ▼           ▼           ▼
        TextHandler  ButtonHandler  FallbackHandler
               │           │           │
               └─────┬─────┘           │
                     ▼                 ▼
              ┌────────────┐    ┌────────────┐
              │   Redis    │    │ PostgreSQL  │
              │ (Sessions) │    │   (Data)   │
              └────────────┘    └────────────┘
```

## Estrutura

```
boost/
├── webhook/        # FastAPI — recebe e valida webhooks do WhatsApp
├── workers/        # Lambda — roteamento e handlers de mensagens
├── infra/          # AWS CDK — toda a infraestrutura como código
├── dashboard/      # React — painel de monitoramento (FlowCore)
├── docs/           # Schema SQL e documentação
└── scripts/        # Scripts auxiliares (LocalStack init)
```

## Quick Start (local)

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais WhatsApp

# 2. Subir stack local
docker compose up -d

# 3. Dashboard
cd dashboard
cp .env.example .env.local
npm install
npm run dev
```

## Deploy AWS

```bash
# Instalar dependências CDK
cd infra
pip install -r requirements.txt

# Bootstrap (primeira vez)
cdk bootstrap aws://ACCOUNT_ID/us-east-1

# Deploy todas as stacks
cdk deploy --all
```

## Componentes

### Webhook Handler (`/webhook`)
- FastAPI com validação HMAC-SHA256 da assinatura Meta
- Resposta em < 500ms (processamento assíncrono via `BackgroundTasks`)
- Publica envelope padronizado no SQS FIFO

### Message Router (`/workers`)
- Lambda Python consumindo SQS (batch de 5 mensagens)
- Handlers por tipo: `text`, `button`, `interactive`, `audio`, `fallback`
- Gestão de sessão por conversa via Redis (TTL 30min)
- Logs estruturados JSON para CloudWatch

### Sales Agent (`/workers/agents`) — LangChain
- Agente de vendas WhatsApp com LangChain + OpenAI
- 12 prompt templates organizados por fase do funil (greeting, qualification, pitch, objection, closing, checkout)
- 8 tools integráveis: consultar catálogo, estoque, frete, CRM, transferir humano, agendar follow-up
- Classificador de intenção (10 categorias) com transferência automática para humano
- Memória de conversa persistida no Redis (últimos 20 turnos por sessão)
- Toggle `USE_AI_AGENT=true/false` no `.env` para A/B test contra o handler estático

Docs completas: [docs/sales_agent.md](docs/sales_agent.md)

### Dashboard (`/dashboard`)
- React + Tailwind + Supabase Realtime
- Páginas: Dashboard, Flows, Mensagens, DLQ, Configurações
- Atualização automática a cada 30s
- Feed de mensagens em tempo real via Supabase Realtime

### Infraestrutura (`/infra`)
- AWS CDK (Python)
- ECS Fargate para o webhook
- Lambda para workers
- SQS FIFO com DLQ (3 retries)
- ElastiCache Redis
- RDS PostgreSQL com backup diário

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `WHATSAPP_APP_SECRET` | Secret do app Meta para validação HMAC |
| `WHATSAPP_VERIFY_TOKEN` | Token de verificação do webhook |
| `WHATSAPP_PHONE_NUMBER_ID` | ID do número no WhatsApp Business |
| `WHATSAPP_ACCESS_TOKEN` | Token de acesso à Cloud API |
| `SQS_QUEUE_URL` | URL da fila SQS FIFO |
| `REDIS_URL` | URL do Redis (ex: `redis://localhost:6379`) |
| `DATABASE_URL` | DSN PostgreSQL |

## Custo estimado (MVP)

| Serviço | Custo/mês (50k msg) |
|---------|---------------------|
| Lambda | ~$0 (free tier) |
| SQS | ~$0.02 |
| ElastiCache t3.micro | ~$12 |
| RDS t3.micro | ~$15 |
| ECS Fargate (0.25 vCPU) | ~$8 |
| **Total** | **~$35/mês** |
