"""
Integrações externas do SDR — Evolution API, CRM, Calendly, Slack.

Todos os clientes são async (httpx) e leem credenciais do ambiente.
"""
from integrations.calendly import CalendlyClient, CalendlyError
from integrations.crm import (
    CRMError,
    HubSpotClient,
    PipedriveClient,
    get_crm_client,
)
from integrations.evolution import EvolutionAPIError, EvolutionClient
from integrations.slack import SlackClient, SlackError

__all__ = [
    "EvolutionClient",
    "EvolutionAPIError",
    "HubSpotClient",
    "PipedriveClient",
    "CRMError",
    "get_crm_client",
    "CalendlyClient",
    "CalendlyError",
    "SlackClient",
    "SlackError",
]
