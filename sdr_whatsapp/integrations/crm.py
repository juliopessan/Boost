"""
CRM client — integração com HubSpot (padrão) ou Pipedrive.

HubSpot é o default por ser o mais comum em operações de SDR.
Para trocar, basta setar CRM_PROVIDER=pipedrive no .env.

Endpoints:
- HubSpot CRM API v3: https://developers.hubspot.com/docs/api/crm/contacts
- Pipedrive API v1:   https://developers.pipedrive.com/docs/api/v1
"""

import os
import logging
from typing import Any, Literal

import httpx

log = logging.getLogger(__name__)


class CRMError(RuntimeError):
    pass


# ─────────────────────── HUBSPOT ───────────────────────


class HubSpotClient:
    """
    Cliente HubSpot CRM.

    Mapeamento de campos custom (criar antes no portal HubSpot):
    - bant_score (number, 0-4)
    - sdr_stage (single-line text: quebra-gelo, descoberta, qualificacao, cta, encerrado)
    - sdr_notes (multi-line text)
    """

    BASE = "https://api.hubapi.com"

    def __init__(self, token: str | None = None, timeout: float = 10.0):
        self.token = token or os.environ["HUBSPOT_TOKEN"]
        self.timeout = timeout

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def get_lead_by_phone(self, phone: str) -> dict[str, Any] | None:
        """Busca contato HubSpot pelo telefone (E.164 sem +)."""
        url = f"{self.BASE}/crm/v3/objects/contacts/search"
        payload = {
            "filterGroups": [
                {
                    "filters": [
                        {"propertyName": "phone", "operator": "EQ", "value": phone},
                        {"propertyName": "mobilephone", "operator": "EQ", "value": phone},
                    ]
                }
            ],
            "properties": [
                "firstname", "lastname", "email", "phone", "company",
                "jobtitle", "lifecyclestage", "bant_score", "sdr_stage", "sdr_notes",
            ],
            "limit": 1,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=self.headers)

        if response.status_code >= 400:
            log.error("hubspot.search_failed", extra={"status": response.status_code})
            raise CRMError(f"HubSpot search failed: {response.text[:200]}")

        results = response.json().get("results", [])
        if not results:
            return None

        contact = results[0]
        props = contact.get("properties", {})
        return {
            "id": contact.get("id"),
            "name": " ".join(filter(None, [props.get("firstname"), props.get("lastname")])).strip(),
            "email": props.get("email"),
            "phone": props.get("phone") or props.get("mobilephone"),
            "company": props.get("company"),
            "job_title": props.get("jobtitle"),
            "lifecycle_stage": props.get("lifecyclestage"),
            "bant_score": int(props.get("bant_score") or 0),
            "sdr_stage": props.get("sdr_stage") or "novo",
            "notes": props.get("sdr_notes") or "",
        }

    async def upsert_lead(
        self,
        phone: str,
        stage: str,
        bant_score: int | None = None,
        notes: str | None = None,
        extra_properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Cria ou atualiza contato HubSpot por telefone."""
        existing = await self.get_lead_by_phone(phone)
        properties: dict[str, Any] = {
            "phone": phone,
            "sdr_stage": stage,
        }
        if bant_score is not None:
            properties["bant_score"] = bant_score
        if notes is not None:
            properties["sdr_notes"] = notes
        if extra_properties:
            properties.update(extra_properties)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if existing:
                url = f"{self.BASE}/crm/v3/objects/contacts/{existing['id']}"
                response = await client.patch(url, json={"properties": properties}, headers=self.headers)
            else:
                url = f"{self.BASE}/crm/v3/objects/contacts"
                response = await client.post(url, json={"properties": properties}, headers=self.headers)

        if response.status_code >= 400:
            log.error("hubspot.upsert_failed", extra={"status": response.status_code, "body": response.text[:200]})
            raise CRMError(f"HubSpot upsert failed: {response.text[:200]}")

        log.info("hubspot.lead_upserted", extra={"phone": phone[-4:], "stage": stage})
        return response.json()


# ─────────────────────── PIPEDRIVE ───────────────────────


class PipedriveClient:
    """
    Cliente Pipedrive.
    Usa Persons (contatos) e Deals (oportunidades) — mais B2B-friendly que HubSpot.
    """

    def __init__(self, token: str | None = None, base_url: str | None = None, timeout: float = 10.0):
        self.token = token or os.environ["PIPEDRIVE_TOKEN"]
        self.base_url = (base_url or os.environ.get("PIPEDRIVE_URL", "https://api.pipedrive.com/v1")).rstrip("/")
        self.timeout = timeout

    async def get_lead_by_phone(self, phone: str) -> dict[str, Any] | None:
        url = f"{self.base_url}/persons/search"
        params = {"term": phone, "fields": "phone", "exact_match": "true", "api_token": self.token}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)

        if response.status_code >= 400:
            raise CRMError(f"Pipedrive search failed: {response.text[:200]}")

        items = response.json().get("data", {}).get("items", [])
        if not items:
            return None

        person = items[0]["item"]
        return {
            "id": person.get("id"),
            "name": person.get("name"),
            "email": (person.get("emails") or [None])[0],
            "phone": (person.get("phones") or [phone])[0],
            "company": (person.get("organization") or {}).get("name") if person.get("organization") else None,
        }

    async def upsert_lead(
        self,
        phone: str,
        stage: str,
        bant_score: int | None = None,
        notes: str | None = None,
        extra_properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        existing = await self.get_lead_by_phone(phone)
        payload = {
            "phone": [{"value": phone, "primary": True}],
            "visible_to": 3,
        }
        if extra_properties:
            payload.update(extra_properties)

        params = {"api_token": self.token}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if existing:
                url = f"{self.base_url}/persons/{existing['id']}"
                response = await client.put(url, json=payload, params=params)
            else:
                url = f"{self.base_url}/persons"
                response = await client.post(url, json=payload, params=params)

            if response.status_code >= 400:
                raise CRMError(f"Pipedrive upsert failed: {response.text[:200]}")

            person_data = response.json().get("data", {})

            # Adiciona nota com BANT + stage + notes
            if notes or stage or bant_score is not None:
                note_url = f"{self.base_url}/notes"
                note_content = (
                    f"<b>Stage:</b> {stage}<br>"
                    f"<b>BANT:</b> {bant_score if bant_score is not None else 'N/A'}<br>"
                    f"<b>Notes:</b> {notes or ''}"
                )
                await client.post(note_url, json={"person_id": person_data.get("id"), "content": note_content}, params=params)

        log.info("pipedrive.lead_upserted", extra={"phone": phone[-4:], "stage": stage})
        return person_data


# ─────────────────────── FACTORY ───────────────────────


CRMProvider = Literal["hubspot", "pipedrive"]


def get_crm_client(provider: CRMProvider | None = None) -> HubSpotClient | PipedriveClient:
    """Retorna o cliente CRM configurado via env CRM_PROVIDER."""
    provider = provider or os.environ.get("CRM_PROVIDER", "hubspot").lower()  # type: ignore[assignment]
    if provider == "pipedrive":
        return PipedriveClient()
    return HubSpotClient()
