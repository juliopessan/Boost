"""
KeuneSalesAgent — extensão do SalesAgent base com persona, catálogo
e tools específicas da Keune Brasil.

Uso:
    from workers.agents.configs.keune import KeuneSalesAgent
    agent = KeuneSalesAgent()
    response = agent.respond(user_message, session_state)
"""
from typing import Any

import structlog
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from workers.agents.configs.keune.persona import (
    KEUNE_HUMAN_HANDOFF_TEMPLATES,
    KEUNE_SYSTEM_PROMPT,
)
from workers.agents.configs.keune.tools import KEUNE_TOOLS
from workers.agents.tools.handoff import agendar_followup, transferir_humano

log = structlog.get_logger()


class KeuneSalesAgent:
    """Agente de vendas Keune Brasil (Lara) — extensão do SalesAgent base."""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.3):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.tools = [*KEUNE_TOOLS, transferir_humano, agendar_followup]

        prompt = ChatPromptTemplate.from_messages([
            ("system", KEUNE_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            max_iterations=6,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
        )

    def _build_chat_history(self, session_state: dict) -> list:
        messages = []
        for turn in session_state.get("history", [])[-10:]:
            role = turn.get("role")
            content = turn.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "agent":
                messages.append(AIMessage(content=content))
        return messages

    def _build_context(self, session_state: dict) -> dict[str, str]:
        return {
            "customer_context": str(session_state.get("customer", {})),
            "conversation_history": "(ver mensagens anteriores)",
            "funnel_stage": session_state.get("stage", "greeting"),
            "customer_type": session_state.get("customer_type", "desconhecido"),
            "tools_description": ", ".join(t.name for t in self.tools),
        }

    def respond(self, user_message: str, session_state: dict) -> dict[str, Any]:
        chat_history = self._build_chat_history(session_state)
        context = self._build_context(session_state)

        try:
            result = self.executor.invoke({
                "input": user_message,
                "chat_history": chat_history,
                **context,
            })

            response_text = result.get("output", "")
            tools_used = [
                step[0].tool for step in result.get("intermediate_steps", [])
            ]
            should_handoff = "transferir_humano" in tools_used or "conectar_representante" in tools_used

            log.info(
                "keune_agent.responded",
                tools_used=tools_used,
                handoff=should_handoff,
                stage=context["funnel_stage"],
            )

            return {
                "response": response_text,
                "tools_used": tools_used,
                "new_stage": self._infer_next_stage(session_state, tools_used),
                "should_handoff": should_handoff,
                "customer_type": self._infer_customer_type(session_state, tools_used),
            }

        except Exception as e:
            log.error("keune_agent.error", error=str(e))
            return {
                "response": "Tive um probleminha aqui, pode mandar de novo? 💛",
                "tools_used": [],
                "new_stage": session_state.get("stage", "greeting"),
                "should_handoff": False,
            }

    def _infer_next_stage(self, session_state: dict, tools_used: list[str]) -> str:
        current = session_state.get("stage", "greeting")
        if "transferir_humano" in tools_used or "conectar_representante" in tools_used:
            return "human_handoff"
        if "recomendar_kit_keune" in tools_used:
            return "pitch"
        if "diagnosticar_queixa" in tools_used and current == "greeting":
            return "qualification"
        if "localizar_salao_parceiro" in tools_used:
            return "directing_to_store"
        return current

    def _infer_customer_type(self, session_state: dict, tools_used: list[str]) -> str:
        if "conectar_representante" in tools_used:
            return "B2B"
        if "recomendar_kit_keune" in tools_used or "localizar_salao_parceiro" in tools_used:
            return "B2C"
        return session_state.get("customer_type", "desconhecido")

    @staticmethod
    def handoff_message(reason: str) -> str:
        """Retorna mensagem padrão de transferência Keune por motivo."""
        return KEUNE_HUMAN_HANDOFF_TEMPLATES.get(
            reason, KEUNE_HUMAN_HANDOFF_TEMPLATES["complex_question"]
        )
