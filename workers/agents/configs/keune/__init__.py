from workers.agents.configs.keune.agent import KeuneSalesAgent
from workers.agents.configs.keune.catalog import (
    KEUNE_CATALOG,
    KEUNE_KITS_RECOMENDADOS,
    buscar_produtos,
    recomendar_kit,
)
from workers.agents.configs.keune.knowledge import (
    DIAGNOSTICO_CAPILAR,
    KEUNE_FAQ,
    REPRESENTANTES_REGIONAIS,
)
from workers.agents.configs.keune.persona import (
    KEUNE_GREETING_PROMPT,
    KEUNE_HUMAN_HANDOFF_TEMPLATES,
    KEUNE_OBJECTION_PROMPT,
    KEUNE_PITCH_B2C_PROMPT,
    KEUNE_QUALIFICATION_B2B_PROMPT,
    KEUNE_QUALIFICATION_B2C_PROMPT,
    KEUNE_SYSTEM_PROMPT,
)
from workers.agents.configs.keune.tools import KEUNE_TOOLS

__all__ = [
    "KeuneSalesAgent",
    "KEUNE_CATALOG",
    "KEUNE_KITS_RECOMENDADOS",
    "KEUNE_FAQ",
    "KEUNE_TOOLS",
    "KEUNE_SYSTEM_PROMPT",
    "KEUNE_GREETING_PROMPT",
    "KEUNE_QUALIFICATION_B2C_PROMPT",
    "KEUNE_QUALIFICATION_B2B_PROMPT",
    "KEUNE_PITCH_B2C_PROMPT",
    "KEUNE_OBJECTION_PROMPT",
    "KEUNE_HUMAN_HANDOFF_TEMPLATES",
    "DIAGNOSTICO_CAPILAR",
    "REPRESENTANTES_REGIONAIS",
    "buscar_produtos",
    "recomendar_kit",
]
