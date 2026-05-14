"""
Model Router — SDR WhatsApp
Usa Haiku 4.5 (barato, rápido) para classificar a mensagem
e decide qual modelo responde, economizando ~66% nos tokens de entrada.
"""

import json
import anthropic
from sdr_config import (
    MODELS,
    CATEGORY_TO_MODEL,
    ROUTER_SYSTEM_PROMPT,
    COST_PER_MTok,
)

client = anthropic.Anthropic()  # ANTHROPIC_API_KEY via env


# ─── TIPOS ────────────────────────────────────────────────────────────────────

VALID_CATEGORIES = {
    "simple_greeting",
    "qualification",
    "objection_simple",
    "objection_complex",
    "booking_request",
    "out_of_scope",
}


# ─── ROUTER PRINCIPAL ─────────────────────────────────────────────────────────

def classify_message(message: str) -> dict:
    """
    Classifica a mensagem do lead usando Haiku (custo ~3x menor que Sonnet).
    Retorna: { category, model_to_use, cost_estimate_usd }
    """
    response = client.messages.create(
        model=MODELS["router"],
        max_tokens=50,  # só precisa do JSON pequeno
        system=ROUTER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": message}],
    )

    raw = response.content[0].text.strip()

    try:
        data = json.loads(raw)
        category = data.get("category", "qualification")
    except (json.JSONDecodeError, AttributeError):
        category = "qualification"  # fallback seguro

    if category not in VALID_CATEGORIES:
        category = "qualification"

    model_to_use = CATEGORY_TO_MODEL[category]

    # Custo real desta classificação
    input_tokens  = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    rates = COST_PER_MTok[MODELS["router"]]
    cost = (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000

    return {
        "category":     category,
        "model_to_use": model_to_use,
        "router_cost":  round(cost, 6),
        "router_tokens": {
            "input": input_tokens,
            "output": output_tokens,
        },
    }


# ─── LOGGING DE CUSTO ─────────────────────────────────────────────────────────

def estimate_turn_cost(model: str, usage) -> dict:
    """
    Calcula custo de um turn com base no uso reportado pela API.
    Suporta cache_read_input_tokens quando disponível.
    """
    rates = COST_PER_MTok.get(model, COST_PER_MTok[MODELS["sdr"]])

    input_tokens       = getattr(usage, "input_tokens", 0)
    output_tokens      = getattr(usage, "output_tokens", 0)
    cache_read_tokens  = getattr(usage, "cache_read_input_tokens", 0)
    cache_write_tokens = getattr(usage, "cache_creation_input_tokens", 0)

    # Tokens de input que NÃO vieram do cache
    billable_input = input_tokens - cache_read_tokens

    cost_input        = (billable_input    * rates["input"])        / 1_000_000
    cost_cache_read   = (cache_read_tokens * rates["cache_read"])   / 1_000_000
    cost_cache_write  = (cache_write_tokens * rates["input"] * 1.25) / 1_000_000
    cost_output       = (output_tokens     * rates["output"])       / 1_000_000

    total = cost_input + cost_cache_read + cost_cache_write + cost_output

    return {
        "model":            model,
        "tokens_input":     input_tokens,
        "tokens_output":    output_tokens,
        "tokens_cached":    cache_read_tokens,
        "tokens_cached_write": cache_write_tokens,
        "cost_usd":         round(total, 6),
        "savings_vs_nocache": round(
            (cache_read_tokens * (rates["input"] - rates["cache_read"])) / 1_000_000, 6
        ),
    }
