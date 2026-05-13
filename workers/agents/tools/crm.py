"""Tools de CRM — registro de leads, oportunidades, contexto do cliente."""
from typing import Any
from langchain_core.tools import tool
import structlog

log = structlog.get_logger()


@tool
def buscar_cliente(phone_hash: str) -> dict[str, Any]:
    """
    Busca dados do cliente no CRM pelo hash do telefone.

    Args:
        phone_hash: Hash SHA-256 do telefone do cliente

    Returns:
        Dict com dados do cliente ou {"is_new": true} se for novo
    """
    log.info("tool.crm_lookup", phone_hash=phone_hash[:8])
    # TODO: integrar com CRM real (HubSpot, Pipedrive, RD Station, etc)
    return {
        "is_new": True,
        "name": None,
        "previous_orders": 0,
        "last_interaction": None,
        "tags": [],
    }


@tool
def registrar_lead(
    phone_hash: str,
    name: str,
    qualification: dict[str, Any],
    source: str = "whatsapp",
) -> dict[str, Any]:
    """
    Registra um novo lead qualificado no CRM.

    Args:
        phone_hash: Hash do telefone
        name: Nome do cliente
        qualification: Dict com need, urgency, volume, decision_maker
        source: Origem do lead (default: whatsapp)

    Returns:
        Dict com lead_id e score de qualificação
    """
    log.info("tool.lead_registered", phone_hash=phone_hash[:8], name=name)
    return {
        "lead_id": "LEAD-12345",
        "score": 75,
        "tier": "warm",
    }


@tool
def criar_oportunidade(
    lead_id: str,
    products: list[str],
    estimated_value: float,
    stage: str = "qualified",
) -> dict[str, Any]:
    """
    Cria oportunidade de venda vinculada ao lead.

    Args:
        lead_id: ID do lead
        products: Lista de IDs dos produtos de interesse
        estimated_value: Valor estimado da oportunidade
        stage: Estágio (qualified, proposal, negotiation, won, lost)

    Returns:
        Dict com opportunity_id
    """
    log.info("tool.opportunity_created", lead_id=lead_id, value=estimated_value)
    return {"opportunity_id": "OPP-67890"}
