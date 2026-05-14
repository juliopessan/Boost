"""
Slack handoff client — notifica time de vendas via Incoming Webhook.

Configuração:
1. Acesse https://api.slack.com/messaging/webhooks
2. Crie um app + incoming webhook no canal #vendas-handoff (ou similar)
3. Cole a URL em SLACK_WEBHOOK_URL no .env

Para Block Kit avançado (com botões): https://api.slack.com/block-kit
"""

import os
import logging
from typing import Any

import httpx

log = logging.getLogger(__name__)


class SlackError(RuntimeError):
    pass


class SlackClient:
    def __init__(self, webhook_url: str | None = None, timeout: float = 8.0):
        self.webhook_url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL", "")
        self.timeout = timeout

    async def send_handoff(
        self,
        phone: str,
        reason: str,
        lead_name: str | None = None,
        company: str | None = None,
        bant_score: int | None = None,
        conversation_summary: str | None = None,
        priority: str = "medium",
    ) -> dict[str, Any]:
        """
        Notifica time de vendas sobre handoff de lead via Block Kit.

        Args:
            phone: telefone do lead (E.164)
            reason: motivo da transferência
            lead_name, company: contexto do lead (se disponível)
            bant_score: 0-4 (do CRM)
            conversation_summary: resumo do histórico (opcional)
            priority: low | medium | high | urgent

        Returns:
            {"ok": bool, "status_code": int}
        """
        if not self.webhook_url:
            log.warning("slack.webhook_not_configured")
            return {"ok": False, "reason": "webhook_not_configured"}

        priority_emoji = {
            "low": "⚪",
            "medium": "🟡",
            "high": "🟠",
            "urgent": "🔴",
        }.get(priority, "🟡")

        # Header
        blocks: list[dict[str, Any]] = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{priority_emoji} Novo Handoff de SDR"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Lead:*\n{lead_name or 'Sem nome'}"},
                    {"type": "mrkdwn", "text": f"*Telefone:*\n`{phone}`"},
                    {"type": "mrkdwn", "text": f"*Empresa:*\n{company or '—'}"},
                    {"type": "mrkdwn", "text": f"*BANT:*\n{bant_score if bant_score is not None else '—'}/4"},
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Motivo do handoff:*\n{reason}"},
            },
        ]

        # Resumo da conversa
        if conversation_summary:
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Resumo da conversa:*\n>{conversation_summary}"},
                }
            )

        # Botão para abrir WhatsApp Web direto
        blocks.append(
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Abrir WhatsApp"},
                        "url": f"https://wa.me/{phone}",
                        "style": "primary",
                    }
                ],
            }
        )

        payload = {
            "text": f"Handoff SDR — {lead_name or phone} ({priority})",
            "blocks": blocks,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.webhook_url, json=payload)

        ok = response.status_code == 200
        if not ok:
            log.error("slack.send_failed", extra={"status": response.status_code, "body": response.text[:200]})
        else:
            log.info("slack.handoff_sent", extra={"phone": phone[-4:], "priority": priority})

        return {"ok": ok, "status_code": response.status_code}
