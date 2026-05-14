"""
Context Compactor — SDR WhatsApp
Monitora o uso de tokens e compacta o histórico quando atinge 40% da context window.
Estratégia: resume turns antigos → preserva turns recentes integralmente.

Por que 40%?
  - System prompt cacheado (~2k tokens)
  - Tool schemas (~1k tokens)
  - Reserva para resposta do agente (~2k tokens)
  → Compactar cedo evita truncamento forçado pela API
"""

import anthropic
from sdr_config import (
    MODELS,
    COMPACTION_TRIGGER_TOKENS,
    CONTEXT_WINDOW_TOKENS,
    SDR_SYSTEM_PROMPT,
)

client = anthropic.Anthropic()


# ─── COMPACTION SYSTEM PROMPT (Haiku faz o resumo — barato) ──────────────────

COMPACTION_PROMPT = """
Você vai receber um histórico de conversa entre uma SDR (Sofia) e um lead via WhatsApp.
Sua tarefa: criar um resumo COMPACTO e PRECISO para substituir os turns antigos.

O resumo deve conter:
1. Nome e cargo do lead (se mencionado)
2. Empresa e segmento (se mencionado)
3. Dor/necessidade identificada
4. Objeções levantadas
5. BANT score atual (0-4) e quais critérios foram confirmados
6. Estágio atual da conversa (quebra-gelo/descoberta/qualificacao/cta/encerrado)
7. Próximo passo combinado (se houver)

Formato: parágrafo curto + bullets. Máximo 300 tokens.
Retorne APENAS o resumo, sem introdução.
""".strip()


# ─── CONTADOR DE TOKENS ───────────────────────────────────────────────────────

def count_tokens(messages: list, system: str = "") -> int:
    """
    Usa a Token Count API da Anthropic para contagem precisa.
    Evita heurísticas imprecisas (chars/4 etc.)
    """
    try:
        response = client.messages.count_tokens(
            model=MODELS["sdr"],
            system=system,
            messages=messages,
        )
        return response.input_tokens
    except Exception:
        # Fallback: estimativa grosseira (chars / 4)
        total_chars = len(system)
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total_chars += len(content)
            elif isinstance(content, list):
                for block in content:
                    total_chars += len(str(block.get("text", "")))
        return total_chars // 4


# ─── VERIFICADOR DE THRESHOLD ─────────────────────────────────────────────────

def needs_compaction(messages: list, system: str = SDR_SYSTEM_PROMPT) -> dict:
    """
    Verifica se o histórico já atingiu 40% da context window.
    Retorna dict com status e métricas.
    """
    token_count = count_tokens(messages, system)
    percentage  = token_count / CONTEXT_WINDOW_TOKENS

    return {
        "needs_compaction": token_count >= COMPACTION_TRIGGER_TOKENS,
        "current_tokens":   token_count,
        "threshold_tokens": COMPACTION_TRIGGER_TOKENS,
        "window_tokens":    CONTEXT_WINDOW_TOKENS,
        "usage_percentage": round(percentage * 100, 1),
    }


# ─── COMPACTOR PRINCIPAL ──────────────────────────────────────────────────────

def compact_history(messages: list, preserve_last_n: int = 4) -> list:
    """
    Compacta o histórico preservando os N últimos turns integralmente.

    Estratégia:
      - Turns antigos (0 até -preserve_last_n) → resumidos em 1 mensagem
      - Turns recentes (últimos N) → preservados integralmente

    Args:
        messages: lista de messages do histórico completo
        preserve_last_n: quantos turns recentes preservar sem modificação

    Returns:
        Nova lista de messages compactada
    """
    if len(messages) <= preserve_last_n * 2:
        # Histórico curto demais para compactar — não faz nada
        return messages

    # Separa turns antigos dos recentes
    split_point    = len(messages) - (preserve_last_n * 2)
    old_messages   = messages[:split_point]
    recent_messages = messages[split_point:]

    # Monta o texto dos turns antigos para o Haiku resumir
    history_text = ""
    for msg in old_messages:
        role    = msg["role"].upper()
        content = msg["content"]
        if isinstance(content, list):
            # Extrai só o texto de content blocks
            content = " ".join(
                block.get("text", "") for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        history_text += f"\n[{role}]: {content}"

    # Haiku faz o resumo (custo mínimo)
    summary_response = client.messages.create(
        model=MODELS["router"],  # Haiku — barato para sumarizar
        max_tokens=350,
        system=COMPACTION_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Histórico da conversa para resumir:\n{history_text}"
        }],
    )

    summary_text = summary_response.content[0].text.strip()

    # Monta o histórico compactado
    # → 1 mensagem de sistema com o resumo + turns recentes completos
    compacted_messages = [
        {
            "role": "user",
            "content": (
                f"[RESUMO DO CONTEXTO ANTERIOR — gerado automaticamente]\n\n"
                f"{summary_text}\n\n"
                f"[FIM DO RESUMO — conversa continua abaixo]"
            ),
        },
        {
            "role": "assistant",
            "content": "Entendido. Continuando a conversa com base no contexto acima.",
        },
    ] + recent_messages

    return compacted_messages


# ─── PIPELINE COMPLETO: VERIFICAR + COMPACTAR SE NECESSÁRIO ──────────────────

def maybe_compact(messages: list, system: str = SDR_SYSTEM_PROMPT) -> tuple[list, dict]:
    """
    Verifica e compacta se necessário. Retorna (messages, report).

    Uso:
        messages, report = maybe_compact(messages)
        if report["compacted"]:
            print(f"Compactado: {report['tokens_before']} → {report['tokens_after']} tokens")
    """
    status = needs_compaction(messages, system)

    if not status["needs_compaction"]:
        return messages, {
            "compacted":      False,
            "tokens_current": status["current_tokens"],
            "usage_pct":      status["usage_percentage"],
        }

    tokens_before = status["current_tokens"]
    compacted     = compact_history(messages)
    tokens_after  = count_tokens(compacted, system)

    reduction_pct = round((1 - tokens_after / tokens_before) * 100, 1)

    return compacted, {
        "compacted":       True,
        "tokens_before":   tokens_before,
        "tokens_after":    tokens_after,
        "reduction_pct":   reduction_pct,
        "usage_pct_after": round(tokens_after / CONTEXT_WINDOW_TOKENS * 100, 1),
    }
