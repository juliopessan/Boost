"""
Agente principal de vendas — LangChain AgentExecutor com tools.
Roteia pelo estágio do funil e mantém memória da conversa via Redis.
"""
import json
from typing import Any

import structlog
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from workers.agents.prompts import (
    GREETING_PROMPT,
    OBJECTION_HANDLING_PROMPT,
    PRODUCT_PITCH_PROMPT,
    QUALIFICATION_PROMPT,
    SALES_AGENT_SYSTEM_PROMPT,
)
from workers.agents.tools import ALL_TOOLS

log = structlog.get_logger()


class SalesAgent:
    """Agente de vendas WhatsApp com LangChain."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        company_name: str = "Boost",
        product_category: str = "produtos digitais",
    ):
        self.company_name = company_name
        self.product_category = product_category
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.tools = ALL_TOOLS

        prompt = ChatPromptTemplate.from_messages([
            ("system", SALES_AGENT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            max_iterations=5,
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
        customer = session_state.get("customer", {})
        funnel_stage = session_state.get("stage", "greeting")
        qualified = session_state.get("qualified", {})

        return {
            "company_name": self.company_name,
            "product_category": self.product_category,
            "customer_context": json.dumps(customer, ensure_ascii=False),
            "conversation_history": "(ver mensagens anteriores)",
            "funnel_stage": funnel_stage,
            "tools_description": ", ".join(t.name for t in self.tools),
        }

    def respond(self, user_message: str, session_state: dict) -> dict[str, Any]:
        """
        Processa mensagem do cliente e retorna resposta + estado atualizado.

        Args:
            user_message: Texto enviado pelo cliente
            session_state: Estado da sessão (do Redis)

        Returns:
            Dict com:
            - response: texto da resposta WhatsApp
            - tools_used: lista de tools chamadas
            - new_stage: próximo estágio do funil
            - should_handoff: True se transferiu para humano
        """
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
            should_handoff = "transferir_humano" in tools_used

            log.info(
                "sales_agent.responded",
                tools_used=tools_used,
                handoff=should_handoff,
                response_len=len(response_text),
            )

            return {
                "response": response_text,
                "tools_used": tools_used,
                "new_stage": self._infer_next_stage(session_state, tools_used),
                "should_handoff": should_handoff,
            }

        except Exception as e:
            log.error("sales_agent.error", error=str(e))
            return {
                "response": "Desculpa, tive um problema técnico aqui 😅 Pode mandar de novo?",
                "tools_used": [],
                "new_stage": session_state.get("stage", "greeting"),
                "should_handoff": False,
            }

    def _infer_next_stage(self, session_state: dict, tools_used: list[str]) -> str:
        current = session_state.get("stage", "greeting")
        if "transferir_humano" in tools_used:
            return "human_handoff"
        if "registrar_lead" in tools_used and current == "qualification":
            return "pitch"
        if "criar_oportunidade" in tools_used:
            return "negotiation"
        return current
