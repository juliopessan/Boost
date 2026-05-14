"""
Calendly client — cria scheduling links de uso único (one-off invites)
e busca o link estático fallback do event_type configurado.

Docs:
- Single-Use Scheduling Links: https://developer.calendly.com/api-docs/9883e2a2306a4-create-a-single-use-scheduling-link
- Event Types: https://developer.calendly.com/api-docs/8a90e35d0bc6f-list-user-s-event-types
"""

import os
import logging
from typing import Any

import httpx

log = logging.getLogger(__name__)


class CalendlyError(RuntimeError):
    pass


class CalendlyClient:
    BASE = "https://api.calendly.com"

    def __init__(
        self,
        token: str | None = None,
        event_type_uri: str | None = None,
        fallback_url: str | None = None,
        timeout: float = 10.0,
    ):
        self.token = token or os.environ["CALENDLY_TOKEN"]
        # URI completa do event_type (ex: https://api.calendly.com/event_types/ABCD-1234)
        self.event_type_uri = event_type_uri or os.environ.get("CALENDLY_EVENT_TYPE_URI", "")
        # Link público fallback (ex: https://calendly.com/sua-empresa/20min)
        self.fallback_url = fallback_url or os.environ.get(
            "CALENDLY_FALLBACK_URL", "https://calendly.com/sua-empresa/20min"
        )
        self.timeout = timeout

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def create_single_use_link(self, max_event_count: int = 1) -> dict[str, Any]:
        """
        Cria link Calendly de uso único — após o lead agendar, o link expira.
        Útil para tracking de conversão por lead.

        Returns:
            { booking_url, owner_type, owner_uri }
        """
        if not self.event_type_uri:
            log.warning("calendly.no_event_type_uri — usando fallback público")
            return {"booking_url": self.fallback_url, "is_fallback": True}

        url = f"{self.BASE}/scheduling_links"
        payload = {
            "max_event_count": max_event_count,
            "owner": self.event_type_uri,
            "owner_type": "EventType",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=self.headers)

        if response.status_code >= 400:
            log.error("calendly.create_link_failed", extra={"status": response.status_code, "body": response.text[:200]})
            # Fallback gracioso
            return {"booking_url": self.fallback_url, "is_fallback": True, "error": response.text[:200]}

        data = response.json().get("resource", {})
        log.info("calendly.single_use_link_created", extra={"booking_url": data.get("booking_url")})
        return {
            "booking_url": data.get("booking_url"),
            "owner_type": data.get("owner_type"),
            "owner_uri": data.get("owner"),
            "is_fallback": False,
        }

    async def get_user_info(self) -> dict[str, Any]:
        """Retorna info do usuário Calendly autenticado (útil para validar token)."""
        url = f"{self.BASE}/users/me"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get("resource", {})
