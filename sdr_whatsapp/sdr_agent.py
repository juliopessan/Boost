"""
SDR Agent Principal — SDR WhatsApp
Orquestra: prompt caching + model router + context compaction + Managed Agents API

Fluxo por mensagem recebida:
  1. Classifica mensagem (Haiku — barato)
  2. Verifica contexto → compacta se ≥40% da context window
  3. Chama modelo correto com cache no system prompt
  4. Executa tool calls retornadas
  5. Loga custo detalhado por turn
"""

import os
import json
import asyncio
import logging
import anthropic
from datetime import datetime

from sdr_config import SDR_SYSTEM_PROMPT, MODELS, CACHE_TTL
from model_router import classify_message, estimate_turn_cost
from context_compactor import maybe_compact

from integrations import (
    CalendlyClient,
    EvolutionClient,
    SlackClient,
    get_crm_client,
)

log = logging.getLogger(__name__)


# ─── CLIENTE ──────────────────────────────────────────────────────────────────

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


# ─── INTEGRAÇÕES (lazy singletons) ────────────────────────────────────────────

_evolution: EvolutionClient | None = None
_calendly: CalendlyClient | None = None
_slack: SlackClient | None = None
_crm = None


def _get_evolution() -> EvolutionClient:
    global _evolution
    if _evolution is None:
        _evolution = EvolutionClient()
    return _evolution


def _get_calendly() -> CalendlyClient:
    global _calendly
    if _calendly is None:
        _calendly = CalendlyClient()
    return _calendly


def _get_slack() -> SlackClient:
    global _slack
    if _slack is None:
        _slack = SlackClient()
    return _slack


def _get_crm():
    global _crm
    if _crm is None:
        _crm = get_crm_client()
    return _crm


# ─── TOOL DEFINITIONS ────────────────────────────────────────────────────────

SDR_TOOLS = [
    {
        "name": "send_whatsapp_message",
        "description": "Envia uma mensagem de texto ao lead via WhatsApp (Evolution API)",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone":   {"type": "string", "description": "Número E.164 ex: 5511999999999"},
                "message": {"type": "string", "description": "Texto da mensagem"},
            },
            "required": ["phone", "message"],
        },
    },
    {
        "name": "get_lead_context",
        "description": "Busca dados do lead no CRM (nome, cargo, empresa, histórico)",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone": {"type": "string"},
            },
            "required": ["phone"],
        },
    },
    {
        "name": "book_meeting",
        "description": "Agenda uma call de 20 min no Calendly e envia o link ao lead",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone":          {"type": "string"},
                "lead_name":      {"type": "string"},
                "preferred_time": {"type": "string", "description": "ISO 8601 ou descrição natural"},
            },
            "required": ["phone", "lead_name"],
        },
    },
    {
        "name": "update_crm",
        "description": "Atualiza status, BANT score e notas do lead no CRM",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone":      {"type": "string"},
                "stage":      {"type": "string", "enum": ["quebra-gelo", "descoberta", "qualificacao", "cta", "encerrado"]},
                "bant_score": {"type": "integer", "minimum": 0, "maximum": 4},
                "notes":      {"type": "string"},
            },
            "required": ["phone", "stage"],
        },
    },
    {
        "name": "handoff_to_human",
        "description": "Transfere a conversa para um vendedor humano com contexto completo",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone":  {"type": "string"},
                "reason": {"type": "string", "description": "Motivo da transferência"},
            },
            "required": ["phone", "reason"],
        },
    },
]


# ─── EXECUTOR DE TOOLS (você implementa a integração real aqui) ───────────────

async def execute_tool(tool_name: str, tool_input: dict) -> str:
    """
    Executa a tool real conectando às integrações reais:
    Evolution API, HubSpot/Pipedrive, Calendly, Slack.

    Retorna sempre uma string JSON com o resultado para o agente continuar.
    Erros são capturados e retornados como JSON com chave "error".
    """
    try:
        if tool_name == "send_whatsapp_message":
            phone = tool_input["phone"]
            message = tool_input["message"]

            evolution = _get_evolution()
            # UX humano: typing indicator antes de enviar
            try:
                await evolution.send_typing_indicator(phone, duration_ms=1500)
            except Exception as e:
                log.warning(f"typing indicator falhou: {e}")

            result = await evolution.send_text(phone, message)
            print(f"📱 WhatsApp → {phone}: {message[:80]}")
            return json.dumps({
                "status": "sent",
                "phone": phone,
                "message_id": result.get("key", {}).get("id"),
            })

        elif tool_name == "get_lead_context":
            phone = tool_input["phone"]
            crm = _get_crm()
            lead = await crm.get_lead_by_phone(phone)

            if lead is None:
                return json.dumps({
                    "phone": phone,
                    "found": False,
                    "stage": "novo",
                    "message": "Lead não encontrado no CRM — primeiro contato",
                })

            return json.dumps({"found": True, **lead})

        elif tool_name == "book_meeting":
            phone = tool_input["phone"]
            lead_name = tool_input.get("lead_name", "Lead")
            preferred_time = tool_input.get("preferred_time")

            calendly = _get_calendly()
            link = await calendly.create_single_use_link()

            # Atualiza CRM com link e estágio cta
            try:
                crm = _get_crm()
                await crm.upsert_lead(
                    phone=phone,
                    stage="cta",
                    notes=f"Link Calendly enviado: {link['booking_url']} | Horário preferencial: {preferred_time}",
                )
            except Exception as e:
                log.warning(f"crm update após booking falhou: {e}")

            # Envia link via WhatsApp
            try:
                evolution = _get_evolution()
                await evolution.send_text(
                    phone=phone,
                    message=(
                        f"Perfeito, {lead_name.split()[0] if lead_name else 'tudo certo'}! "
                        f"Aqui está o link para agendar nossa call de 20 min:\n\n"
                        f"{link['booking_url']}\n\n"
                        f"Escolhe o horário que melhor te encaixa 😉"
                    ),
                    link_preview=True,
                )
            except Exception as e:
                log.warning(f"envio do link falhou: {e}")

            return json.dumps({
                "status": "scheduled",
                "meeting_url": link["booking_url"],
                "is_fallback": link.get("is_fallback", False),
            })

        elif tool_name == "update_crm":
            crm = _get_crm()
            result = await crm.upsert_lead(
                phone=tool_input["phone"],
                stage=tool_input["stage"],
                bant_score=tool_input.get("bant_score"),
                notes=tool_input.get("notes"),
            )
            print(f"📊 CRM atualizado: {tool_input.get('stage')} BANT={tool_input.get('bant_score')}")
            return json.dumps({
                "status": "updated",
                "crm_id": result.get("id") or result.get("data", {}).get("id"),
            })

        elif tool_name == "handoff_to_human":
            phone = tool_input["phone"]
            reason = tool_input["reason"]

            # Busca contexto do lead pra enriquecer notificação
            lead_info: dict = {}
            try:
                crm = _get_crm()
                lead = await crm.get_lead_by_phone(phone)
                if lead:
                    lead_info = lead
            except Exception as e:
                log.warning(f"lookup lead pre-handoff falhou: {e}")

            # Notifica Slack
            slack = _get_slack()
            slack_result = await slack.send_handoff(
                phone=phone,
                reason=reason,
                lead_name=lead_info.get("name"),
                company=lead_info.get("company"),
                bant_score=lead_info.get("bant_score"),
                priority="high" if "urgente" in reason.lower() or "reclamação" in reason.lower() else "medium",
            )

            # Marca estágio "encerrado" no CRM
            try:
                crm = _get_crm()
                await crm.upsert_lead(
                    phone=phone,
                    stage="encerrado",
                    notes=f"Handoff humano. Motivo: {reason}",
                )
            except Exception as e:
                log.warning(f"crm update no handoff falhou: {e}")

            print(f"🚨 Handoff: {reason}")
            return json.dumps({
                "status": "handoff_initiated",
                "slack_notified": slack_result.get("ok", False),
                "reason": reason,
            })

        return json.dumps({"error": f"Tool {tool_name} não implementada"})

    except Exception as e:
        log.error(f"tool_execution_failed: {tool_name} — {e}")
        return json.dumps({"error": str(e), "tool": tool_name})


# ─── SDR AGENT — TURN ÚNICO ───────────────────────────────────────────────────

async def process_message(
    phone:    str,
    message:  str,
    history:  list,           # histórico de messages da conversa
    cost_log: list | None = None,  # acumulador de custo opcional
) -> dict:
    """
    Processa uma mensagem recebida do lead.

    Args:
        phone:    número do lead (E.164)
        message:  texto recebido via WhatsApp
        history:  histórico completo [{role, content}, ...]
        cost_log: lista para acumular métricas de custo

    Returns:
        {
          response_text: str,        # o que o agente respondeu
          updated_history: list,     # histórico atualizado
          routing: dict,             # decisão de routing
          compaction: dict,          # relatório de compaction
          cost: dict,                # custo deste turn
        }
    """
    if cost_log is None:
        cost_log = []

    # ── 1. Classifica com Haiku (barato) ──────────────────────────────────────
    routing = classify_message(message)
    cost_log.append({
        "step":  "router",
        "model": MODELS["router"],
        "cost":  routing["router_cost"],
    })
    print(f"🔀 Router → {routing['category']} → modelo: {routing['model_to_use'].split('-')[1]}")

    # ── 2. Adiciona mensagem do lead ao histórico ──────────────────────────────
    history.append({"role": "user", "content": message})

    # ── 3. Compacta contexto se necessário (≥40% da context window) ───────────
    history, compaction_report = maybe_compact(history)
    if compaction_report["compacted"]:
        print(
            f"🗜️  Contexto compactado: "
            f"{compaction_report['tokens_before']} → {compaction_report['tokens_after']} tokens "
            f"(-{compaction_report['reduction_pct']}%)"
        )

    # ── 4. Prepara system prompt com cache_control ─────────────────────────────
    # O system prompt É ESTÁTICO → cachear integralmente → -90% no próximo turn
    system_with_cache = [
        {
            "type": "text",
            "text": SDR_SYSTEM_PROMPT,
            "cache_control": {
                "type": "ephemeral",
                "ttl":  CACHE_TTL,   # "1h" para SDR (msgs chegam espaçadas)
            },
        }
    ]

    model = routing["model_to_use"]

    # ── 5. Agentic loop com tool use ──────────────────────────────────────────
    final_text = ""
    tool_iterations = 0
    MAX_TOOL_ITERATIONS = 5   # evita loops infinitos

    while tool_iterations < MAX_TOOL_ITERATIONS:
        tool_iterations += 1

        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_with_cache,
            tools=SDR_TOOLS,
            messages=history,
            extra_headers={
                # Necessário para prompt caching com TTL 1h
                "anthropic-beta": "extended-cache-ttl-2025-04-11",
            },
        )

        # Loga custo deste turn
        turn_cost = estimate_turn_cost(model, response.usage)
        cost_log.append({"step": f"sdr_turn_{tool_iterations}", **turn_cost})

        # Adiciona resposta ao histórico
        history.append({"role": "assistant", "content": response.content})

        # Verifica stop reason
        if response.stop_reason == "end_turn":
            # Extrai texto da resposta
            for block in response.content:
                if hasattr(block, "text"):
                    final_text = block.text
            break

        if response.stop_reason == "tool_use":
            # Executa todas as tools em paralelo
            tool_results = []
            tool_tasks = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_tasks.append((block.id, block.name, block.input))

            # Execução paralela das tools
            results = await asyncio.gather(*[
                execute_tool(name, inp) for _, name, inp in tool_tasks
            ])

            for (tool_use_id, tool_name, _), result in zip(tool_tasks, results):
                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": tool_use_id,
                    "content":     result,
                })
                print(f"🔧 Tool: {tool_name} → {result[:80]}...")

            history.append({"role": "user", "content": tool_results})
            continue

        # Qualquer outro stop reason — encerra o loop
        break

    # ── 6. Calcula custo total do turn ────────────────────────────────────────
    total_cost    = sum(c.get("cost_usd", c.get("cost", 0)) for c in cost_log)
    total_savings = sum(c.get("savings_vs_nocache", 0) for c in cost_log)

    cost_summary = {
        "total_usd":    round(total_cost, 6),
        "savings_usd":  round(total_savings, 6),
        "detail":       cost_log,
        "timestamp":    datetime.utcnow().isoformat(),
    }

    print(f"💰 Custo turn: ${cost_summary['total_usd']:.5f} | Economia cache: ${cost_summary['savings_usd']:.5f}")

    return {
        "response_text":    final_text,
        "updated_history":  history,
        "routing":          routing,
        "compaction":       compaction_report,
        "cost":             cost_summary,
    }
