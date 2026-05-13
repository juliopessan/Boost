"""Chain de classificação de intenção — primeira camada antes de rotear."""
import json
from typing import Any

import structlog
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from workers.agents.prompts import INTENT_CLASSIFIER_PROMPT

log = structlog.get_logger()


class IntentClassifier:
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.0):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_template(INTENT_CLASSIFIER_PROMPT)
        self.parser = JsonOutputParser()
        self.chain = self.prompt | self.llm | self.parser

    def classify(
        self,
        user_message: str,
        current_stage: str = "unknown",
        last_agent_message: str = "",
    ) -> dict[str, Any]:
        try:
            result = self.chain.invoke({
                "user_message": user_message,
                "current_stage": current_stage,
                "last_agent_message": last_agent_message,
            })
            log.info("classifier.result", intent=result.get("intent"), confidence=result.get("confidence"))
            return result
        except Exception as e:
            log.error("classifier.error", error=str(e))
            return {
                "intent": "unclear",
                "confidence": 0.0,
                "extracted_entities": {},
                "should_transfer_to_human": False,
                "reasoning": f"Erro na classificação: {e}",
            }
