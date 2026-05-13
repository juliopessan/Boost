"""Tool de transferência para humano e ações sensíveis."""
from typing import Any, Literal
from langchain_core.tools import tool
import structlog

log = structlog.get_logger()


@tool
def transferir_humano(
    phone_hash: str,
    reason: Literal["customer_request", "complaint", "complex_question", "abuse", "post_sale"],
    summary: str,
    priority: Literal["low", "medium", "high", "urgent"] = "medium",
) -> dict[str, Any]:
    """
    Transfere a conversa para um atendente humano e abre ticket.

    Use SEMPRE QUE:
    - Cliente pedir explicitamente para falar com humano
    - Detectar reclamação séria ou ameaça (Procon, processo, etc.)
    - Receber abuso/ofensa
    - Não souber responder uma dúvida sobre pedido existente
    - Pós-venda com problema (entrega, troca, NF)

    Args:
        phone_hash: Hash do telefone do cliente
        reason: Motivo categorizado da transferência
        summary: Resumo do contexto em 1-2 frases para o atendente
        priority: Prioridade do ticket (urgent para reclamações/abuso)

    Returns:
        Dict com ticket_id e prazo estimado de atendimento
    """
    log.info(
        "tool.human_handoff",
        phone_hash=phone_hash[:8],
        reason=reason,
        priority=priority,
    )
    # TODO: integrar com sistema de ticket real (Zendesk, Freshdesk, etc)
    return {
        "ticket_id": "TKT-99999",
        "estimated_response_minutes": 15 if priority in ("high", "urgent") else 60,
        "agent_pool": "vendas" if reason == "customer_request" else "atendimento",
    }


@tool
def agendar_followup(
    phone_hash: str,
    when: str,
    reason: str,
) -> dict[str, Any]:
    """
    Agenda um follow-up automático com o lead.

    Use quando o cliente disser:
    - "Te chamo depois"
    - "Vou pensar"
    - "Me chama semana que vem"

    Args:
        phone_hash: Hash do telefone
        when: Quando contatar (ex: "2026-05-15T10:00:00" ou "in_3_days")
        reason: Motivo do follow-up

    Returns:
        Dict com followup_id e horário confirmado
    """
    log.info("tool.followup_scheduled", phone_hash=phone_hash[:8], when=when)
    return {
        "followup_id": "FUP-11111",
        "scheduled_for": when,
    }
