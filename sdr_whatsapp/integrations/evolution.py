"""
Evolution API client — envia mensagens WhatsApp via Baileys.

Docs: https://doc.evolution-api.com/
"""

import logging
import urllib.parse
from typing import Any

import httpx

from secrets import get_secret, mask_secret

log = logging.getLogger(__name__)


class EvolutionAPIError(RuntimeError):
    """Erro retornado pela Evolution API."""


class EvolutionClient:
    """
    Cliente Evolution API (Baileys).

    Credenciais são carregadas via `secrets.get_secret()` que suporta:
      - .env local (desenvolvimento)
      - AWS Secrets Manager (produção)
      - AWS Parameter Store (staging)

    Em produção, NUNCA passe credenciais via construtor — deixe o `get_secret`
    resolver do backend configurado.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        instance: str | None = None,
        instance_token: str | None = None,
        timeout: float = 10.0,
    ):
        self.base_url = (base_url or get_secret("EVOLUTION_API_URL")).rstrip("/")
        self.api_key = api_key or get_secret("EVOLUTION_API_KEY")
        self.instance = instance or get_secret("EVOLUTION_INSTANCE")
        # Instance Token é OPCIONAL (alguns endpoints exigem em vez da API key global)
        self.instance_token = instance_token or get_secret("EVOLUTION_INSTANCE_TOKEN", required=False)
        self.timeout = timeout

        log.info(
            "evolution.client_initialized",
            extra={
                "base_url": self.base_url,
                "instance": self.instance,
                "api_key": mask_secret(self.api_key),
            },
        )

    @property
    def headers(self) -> dict[str, str]:
        """Auth via apikey (header global)."""
        return {
            "apikey": self.api_key,
            "Content-Type": "application/json",
        }

    @property
    def instance_path(self) -> str:
        """Instância URL-encoded (nomes com espaços precisam disso)."""
        return urllib.parse.quote(self.instance, safe="")

    async def send_text(
        self,
        phone: str,
        message: str,
        delay_ms: int = 1200,
        link_preview: bool = False,
    ) -> dict[str, Any]:
        """
        Envia mensagem de texto via Evolution API.

        Args:
            phone: Número E.164 sem @s.whatsapp.net (ex: 5511999999999)
            message: Texto da mensagem
            delay_ms: Atraso simulando digitação humana
            link_preview: Renderizar preview de links

        Returns:
            Resposta JSON da API com message_id e status
        """
        url = f"{self.base_url}/message/sendText/{self.instance_path}"
        payload = {
            "number": phone,
            "text": message,
            "delay": delay_ms,
            "linkPreview": link_preview,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=self.headers)

        if response.status_code >= 400:
            log.error(
                "evolution.send_text_failed",
                extra={"status": response.status_code, "body": response.text[:200]},
            )
            raise EvolutionAPIError(
                f"Evolution API {response.status_code}: {response.text[:200]}"
            )

        data = response.json()
        log.info("evolution.text_sent", extra={"phone": phone[-4:], "id": data.get("key", {}).get("id")})
        return data

    async def send_typing_indicator(self, phone: str, duration_ms: int = 2000) -> dict[str, Any]:
        """Mostra 'digitando...' antes de enviar mensagem (UX humano)."""
        url = f"{self.base_url}/chat/sendPresence/{self.instance_path}"
        payload = {"number": phone, "presence": "composing", "delay": duration_ms}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=self.headers)

        response.raise_for_status()
        return response.json()

    async def check_connection(self) -> dict[str, Any]:
        """
        Valida que a instância Evolution está conectada ao WhatsApp.
        Retorna estado: 'open' (conectado), 'connecting', 'close' (desconectado).
        """
        url = f"{self.base_url}/instance/connectionState/{self.instance_path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers)

        if response.status_code >= 400:
            raise EvolutionAPIError(
                f"check_connection failed {response.status_code}: {response.text[:200]}"
            )

        data = response.json()
        state = data.get("instance", {}).get("state") or data.get("state")
        log.info("evolution.connection_state", extra={"state": state})
        return {
            "state": state,
            "instance": self.instance,
            "connected": state == "open",
        }

    async def fetch_instance_info(self) -> dict[str, Any]:
        """Retorna info da instância (nome, número, perfil)."""
        url = f"{self.base_url}/instance/fetchInstances"
        params = {"instanceName": self.instance}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()

    async def mark_as_read(self, message_id: str, phone: str) -> dict[str, Any]:
        """Marca mensagem como lida (UX humano — duplo check azul)."""
        url = f"{self.base_url}/chat/markMessageAsRead/{self.instance_path}"
        payload = {
            "read_messages": [
                {"id": message_id, "fromMe": False, "remoteJid": f"{phone}@s.whatsapp.net"}
            ]
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=self.headers)

        response.raise_for_status()
        return response.json()
