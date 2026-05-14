"""
Evolution API client — envia mensagens WhatsApp via Baileys.

Docs: https://doc.evolution-api.com/
"""

import os
import logging
from typing import Any

import httpx

log = logging.getLogger(__name__)


class EvolutionAPIError(RuntimeError):
    """Erro retornado pela Evolution API."""


class EvolutionClient:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        instance: str | None = None,
        timeout: float = 10.0,
    ):
        self.base_url = (base_url or os.environ["EVOLUTION_API_URL"]).rstrip("/")
        self.api_key = api_key or os.environ["EVOLUTION_API_KEY"]
        self.instance = instance or os.environ["EVOLUTION_INSTANCE"]
        self.timeout = timeout

    @property
    def headers(self) -> dict[str, str]:
        return {
            "apikey": self.api_key,
            "Content-Type": "application/json",
        }

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
        url = f"{self.base_url}/message/sendText/{self.instance}"
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
        url = f"{self.base_url}/chat/sendPresence/{self.instance}"
        payload = {"number": phone, "presence": "composing", "delay": duration_ms}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=self.headers)

        response.raise_for_status()
        return response.json()

    async def mark_as_read(self, message_id: str, phone: str) -> dict[str, Any]:
        """Marca mensagem como lida (UX humano — duplo check azul)."""
        url = f"{self.base_url}/chat/markMessageAsRead/{self.instance}"
        payload = {
            "read_messages": [
                {"id": message_id, "fromMe": False, "remoteJid": f"{phone}@s.whatsapp.net"}
            ]
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=self.headers)

        response.raise_for_status()
        return response.json()
