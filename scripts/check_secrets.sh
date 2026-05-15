#!/bin/bash
# Pre-commit hook que bloqueia segredos conhecidos no staging.
# Instalar:
#   cp scripts/check_secrets.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# Padrões verificados:
#  - Tokens HubSpot (pat-na1-*)
#  - Chaves Anthropic (sk-ant-*)
#  - URLs Slack webhook
#  - Padrão da Evolution API key (32 chars alfanuméricos suspeitos)
#  - Strings literais comuns de .env

set -e

# Padrões de segredo (regex egrep)
FORBIDDEN_PATTERNS=(
    'sk-ant-[A-Za-z0-9_-]{20,}'                 # Anthropic key
    'pat-na1-[A-Za-z0-9-]{20,}'                 # HubSpot private app
    'hooks\.slack\.com/services/T[A-Z0-9]+/B'   # Slack webhook
    '[A-F0-9]{12}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}' # UUID estilo Evolution token
    'EVOLUTION_API_KEY=[A-Za-z0-9]{20,}'        # .env staged
    'EVOLUTION_INSTANCE_TOKEN=[A-Za-z0-9-]{20,}'
    'HUBSPOT_TOKEN=[A-Za-z0-9-]{20,}'
    'CALENDLY_TOKEN=[A-Za-z0-9-]{20,}'
    'ANTHROPIC_API_KEY=sk-ant-[A-Za-z0-9_-]{10,}'
)

# Arquivos staged (excluindo .env.example que pode ter placeholders)
STAGED=$(git diff --cached --name-only --diff-filter=ACM | grep -v '\.example$' | grep -v 'scripts/check_secrets\.sh$' || true)

if [ -z "$STAGED" ]; then
    exit 0
fi

FOUND=0
for file in $STAGED; do
    [ -f "$file" ] || continue
    for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
        if git diff --cached "$file" | grep -E "^\+" | grep -Eq "$pattern"; then
            echo "❌ Possível segredo detectado em $file"
            echo "   Padrão: $pattern"
            FOUND=1
        fi
    done
done

# Bloqueia também o arquivo .env diretamente
if echo "$STAGED" | grep -qE '(^|/)\.env$'; then
    echo "❌ Tentando commitar arquivo .env — NÃO PERMITIDO"
    echo "   Adicione ao .gitignore ou use .env.example com placeholders"
    FOUND=1
fi

if [ "$FOUND" -eq 1 ]; then
    echo ""
    echo "🛑 Commit bloqueado. Se for um falso positivo, use:"
    echo "   git commit --no-verify"
    echo ""
    echo "Se um segredo VAZOU, ROTACIONE IMEDIATAMENTE no painel da Evolution:"
    echo "   https://evolution-api-u5ph.srv1633583.hstgr.cloud/manager/login"
    exit 1
fi

exit 0
