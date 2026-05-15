# Política de Segurança — Boost

## Como armazenamos segredos

Este projeto NUNCA armazena credenciais em código. Todas as credenciais (Evolution API key, tokens HubSpot/Calendly/Slack, Anthropic API key) ficam em:

1. **Desenvolvimento local**: arquivo `.env` (gitignored, permissão `600`)
2. **Staging**: AWS Systems Manager Parameter Store
3. **Produção**: AWS Secrets Manager

O módulo [`sdr_whatsapp/secrets.py`](sdr_whatsapp/secrets.py) abstrai a busca de credenciais via `get_secret(name)` e seleciona o backend conforme a env `SECRETS_BACKEND`:

```python
from secrets import get_secret
api_key = get_secret("EVOLUTION_API_KEY")  # transparente entre backends
```

## Camadas de defesa

| Camada | Proteção |
|--------|----------|
| `.gitignore` | `.env`, `.env.local` ignorados (confirmar com `git check-ignore`) |
| Permissão arquivo | `chmod 600 sdr_whatsapp/.env` (somente o usuário lê) |
| Pre-commit hook | [`scripts/check_secrets.sh`](scripts/check_secrets.sh) bloqueia padrões de segredo conhecidos |
| Mask em logs | `secrets.mask_secret()` mostra só os últimos 4 chars em logs |
| Lazy load | Clientes são singletons que só inicializam quando necessário |

### Instalar o pre-commit hook

```bash
cp scripts/check_secrets.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Padrões bloqueados automaticamente:
- `sk-ant-...` (Anthropic)
- `pat-na1-...` (HubSpot private app)
- `hooks.slack.com/services/...` (Slack webhook)
- UUIDs estilo Evolution Instance Token
- Linhas literais como `EVOLUTION_API_KEY=...` em arquivos não-`.example`
- Qualquer arquivo chamado `.env`

## Validar conexão sem expor credenciais

```bash
cd sdr_whatsapp
python -m scripts.check_evolution
```

Saída (mascarada):
```
URL:      https://evolution-api-u5ph.srv1633583.hstgr.cloud
Instance: Julio Pessan
API Key:  ****1Y32
Estado:   open
✅ Instância conectada ao WhatsApp
```

Ou via HTTP enquanto o servidor roda:
```bash
curl http://localhost:8000/evolution-status
# {"ok": true, "state": "open", "instance": "Julio Pessan"}
```

## Rotação de credenciais

**Se você suspeita que uma credencial vazou** (commit acidental, screenshot público, chat de IA, etc.):

### Evolution API
1. Acesse: https://evolution-api-u5ph.srv1633583.hstgr.cloud/manager/login
2. Settings → API Keys → **Regenerate** (invalida a antiga imediatamente)
3. Atualize `EVOLUTION_API_KEY` no `.env` local e nos secret managers
4. Restart do `webhook_server.py` para carregar a nova

### Instance Token (Evolution)
1. No painel: Instances → Julio Pessan → **Regenerate Token**
2. Atualize `EVOLUTION_INSTANCE_TOKEN`

### Anthropic API Key
1. Console: https://console.anthropic.com/settings/keys
2. Revoke a antiga → criar nova
3. Atualizar `ANTHROPIC_API_KEY`

### HubSpot
1. Settings → Integrations → Private Apps → app → **Rotate**
2. Atualizar `HUBSPOT_TOKEN`

### Calendly
1. https://calendly.com/integrations/api_webhooks
2. Revoke → gerar novo PAT
3. Atualizar `CALENDLY_TOKEN`

### Slack Webhook
1. https://api.slack.com/apps → seu app → Incoming Webhooks
2. Revoke o webhook → adicionar novo
3. Atualizar `SLACK_WEBHOOK_URL`

## Auditoria

```bash
# Garantir que .env não está rastreado
git check-ignore -v sdr_whatsapp/.env

# Buscar segredos vazados em todo histórico
git log --all -p -G "(EVOLUTION_API_KEY|EVOLUTION_INSTANCE_TOKEN|sk-ant-)" -- ':!*.example'

# Listar todos os arquivos rastreados que contém "env" ou "secret"
git ls-files | grep -iE "(env|secret|credential|password)"
```

## Em caso de vazamento

Não basta deletar o commit. O Git mantém histórico — qualquer pessoa com clone pode recuperar. Faça nessa ordem:

1. **Rotacione a credencial vazada AGORA** (não espere)
2. Force-push após `git filter-repo` se necessário (raro — só se for segredo crítico no main)
3. Audite logs do provider (Evolution, HubSpot, etc) por uso suspeito
4. Documente o incidente em um issue privado

## Reportando vulnerabilidades

Encontrou uma vulnerabilidade? **Não abra issue público.** Mande email para o owner do repositório com:
- Descrição da falha
- Passos para reproduzir
- Impacto estimado
- Sugestão de correção (se houver)
