from workers.agents.prompts.checkout import (
    CHECKOUT_PROMPT,
    ORDER_CONFIRMATION_PROMPT,
    POST_SALE_PROMPT,
)
from workers.agents.prompts.classifier import (
    HUMAN_HANDOFF_PROMPT,
    INTENT_CLASSIFIER_PROMPT,
)
from workers.agents.prompts.pitch import (
    CLOSING_PROMPT,
    OBJECTION_HANDLING_PROMPT,
    PRODUCT_PITCH_PROMPT,
)
from workers.agents.prompts.qualification import (
    QUALIFICATION_PROMPT,
    QUALIFICATION_QUESTIONS,
)
from workers.agents.prompts.system_persona import (
    GREETING_PROMPT,
    SALES_AGENT_SYSTEM_PROMPT,
)

__all__ = [
    "SALES_AGENT_SYSTEM_PROMPT",
    "GREETING_PROMPT",
    "QUALIFICATION_PROMPT",
    "QUALIFICATION_QUESTIONS",
    "PRODUCT_PITCH_PROMPT",
    "OBJECTION_HANDLING_PROMPT",
    "CLOSING_PROMPT",
    "CHECKOUT_PROMPT",
    "ORDER_CONFIRMATION_PROMPT",
    "POST_SALE_PROMPT",
    "INTENT_CLASSIFIER_PROMPT",
    "HUMAN_HANDOFF_PROMPT",
]
