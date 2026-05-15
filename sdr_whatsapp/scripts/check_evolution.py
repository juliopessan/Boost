"""
Health check da Evolution API.

Uso:
    cd sdr_whatsapp
    python -m scripts.check_evolution

Carrega credenciais do .env local (ou do backend de secrets configurado)
e valida que a instância está conectada ao WhatsApp.

Saída esperada:
    ✓ Evolution API online
    ✓ Instância 'Julio Pessan' conectada
    ✓ Auth válida (apikey ***1Y32)
"""

import asyncio
import os
import sys
from pathlib import Path

# Carregar .env local se python-dotenv estiver disponível
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

# Adiciona o diretório pai ao path para importar `integrations` e `secrets`
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.evolution import EvolutionAPIError, EvolutionClient  # noqa: E402
from secrets import mask_secret  # noqa: E402


async def main() -> int:
    print("🔍 Validando configuração Evolution API...\n")

    try:
        client = EvolutionClient()
    except RuntimeError as e:
        print(f"❌ Credenciais ausentes: {e}")
        return 1

    print(f"  URL:      {client.base_url}")
    print(f"  Instance: {client.instance}")
    print(f"  API Key:  {mask_secret(client.api_key)}")
    print(f"  Token:    {mask_secret(client.instance_token) if client.instance_token else '(não configurado)'}\n")

    # 1. Conexão da instância
    try:
        state = await client.check_connection()
    except EvolutionAPIError as e:
        print(f"❌ Falha ao consultar estado: {e}")
        return 2

    print(f"  Estado:   {state['state']}")
    if state["connected"]:
        print("\n✅ Instância conectada ao WhatsApp")
        return 0

    if state["state"] == "connecting":
        print("\n⚠️  Instância está conectando — aguarde o QR Code ser escaneado")
        return 0

    print("\n❌ Instância desconectada. Faça login no painel da Evolution:")
    print(f"   {client.base_url}/manager/login")
    return 3


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
