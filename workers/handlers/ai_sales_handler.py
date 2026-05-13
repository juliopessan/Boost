"""
Handler de IA — substitui o TextHandler estático por agente de vendas LangChain.
Mantém histórico e estado da conversa no Redis.
"""
import os
from datetime import datetime, timezone

import structlog

from workers.agents import IntentClassifier, SalesAgent
from workers.services.session import SessionService
from workers.services.whatsapp_sender import WhatsAppSender


def _resolve_agent(brand: str, company_name: str, product_category: str):
    """Resolve qual agente usar baseado na marca configurada."""
    if brand.lower() == "keune":
        from workers.agents.configs.keune import KeuneSalesAgent
        return KeuneSalesAgent()
    return SalesAgent(
        company_name=company_name,
        product_category=product_category,
    )

log = structlog.get_logger()


class AISalesHandler:
    """
    Handler de texto que usa LangChain para conversação inteligente.

    Fluxo:
    1. Classifica intenção da mensagem
    2. Se for human_request/complaint → transfere imediato
    3. Caso contrário, passa para SalesAgent (com tools)
    4. Salva turno no histórico Redis
    5. Envia resposta no WhatsApp
    """

    def __init__(
        self,
        session: SessionService,
        sender: WhatsAppSender,
        company_name: str = None,
        product_category: str = None,
    ):
        self.session = session
        self.sender = sender
        self.classifier = IntentClassifier()
        brand = os.getenv("AGENT_BRAND", "default")
        self.agent = _resolve_agent(
            brand=brand,
            company_name=company_name or os.getenv("COMPANY_NAME", "Boost"),
            product_category=product_category or os.getenv("PRODUCT_CATEGORY", "produtos"),
        )

    def handle(self, envelope: dict) -> dict:
        phone = envelope["phone"]
        phone_hash = envelope["phone_hash"]
        message_id = envelope["message_id"]
        body = envelope["payload"].get("text", {}).get("body", "").strip()

        state = self.session.get(phone_hash) or {"stage": "greeting", "history": []}
        self.sender.mark_read(message_id)

        # 1. Classificar intenção
        last_agent_msg = ""
        for turn in reversed(state.get("history", [])):
            if turn.get("role") == "agent":
                last_agent_msg = turn.get("content", "")
                break

        intent_result = self.classifier.classify(
            user_message=body,
            current_stage=state.get("stage", "greeting"),
            last_agent_message=last_agent_msg,
        )

        log.info(
            "ai_handler.intent_classified",
            phone_hash=phone_hash,
            intent=intent_result.get("intent"),
        )

        # 2. Atalho para handoff direto
        if intent_result.get("should_transfer_to_human"):
            self.sender.send_text(
                phone,
                "Entendi! Vou te conectar com nosso atendimento agora. "
                "Um consultor responde em até 15min ⏱️",
            )
            state["stage"] = "human_handoff"
            self.session.set(phone_hash, state)
            return {
                "handled": True,
                "action": "transferred_to_human",
                "intent": intent_result.get("intent"),
            }

        # 3. Invocar SalesAgent
        agent_result = self.agent.respond(user_message=body, session_state=state)
        response_text = agent_result["response"]

        # 4. Enviar resposta no WhatsApp
        if response_text:
            self.sender.send_text(phone, response_text)

        # 5. Atualizar histórico e estado
        state.setdefault("history", []).append({
            "role": "user",
            "content": body,
            "ts": datetime.now(timezone.utc).isoformat(),
            "intent": intent_result.get("intent"),
        })
        state["history"].append({
            "role": "agent",
            "content": response_text,
            "ts": datetime.now(timezone.utc).isoformat(),
            "tools_used": agent_result.get("tools_used", []),
        })
        state["history"] = state["history"][-20:]  # cap em 20 turnos
        state["stage"] = agent_result.get("new_stage", state.get("stage"))
        state["last_intent"] = intent_result.get("intent")

        self.session.set(phone_hash, state, ttl=3600)

        return {
            "handled": True,
            "intent": intent_result.get("intent"),
            "stage": state["stage"],
            "tools_used": agent_result.get("tools_used", []),
            "handoff": agent_result.get("should_handoff", False),
        }
