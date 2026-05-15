"""
Webhook Server — SDR WhatsApp
FastAPI slim: recebe webhook da Evolution API → aciona SDR Agent
Gerencia histórico por número de telefone via dict em memória
(substituir por Redis em produção)
"""

import asyncio
from pathlib import Path

# Carrega .env local antes de qualquer import que consuma secrets
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from collections import defaultdict

from sdr_agent import process_message

app = FastAPI(title="SDR WhatsApp Agent", version="1.0.0")

# Memória de conversa por telefone (substituir por Redis em produção)
conversation_store: dict[str, list] = defaultdict(list)

# Acumulador de custo por telefone (para dashboarding)
cost_store: dict[str, float] = defaultdict(float)


@app.post("/webhook/evolution")
async def evolution_webhook(request: Request):
    """
    Recebe eventos da Evolution API.
    Filtra apenas mensagens de texto recebidas de usuários reais.
    """
    payload = await request.json()

    # Filtra apenas mensagens de texto recebidas (não as enviadas)
    event = payload.get("event", "")
    if event not in ("messages.upsert", "messages.update"):
        return JSONResponse({"status": "ignored", "reason": "not a message event"})

    data    = payload.get("data", {})
    key     = data.get("key", {})
    message = data.get("message", {})

    # Ignora mensagens enviadas pelo próprio agente
    if key.get("fromMe", False):
        return JSONResponse({"status": "ignored", "reason": "own message"})

    phone = key.get("remoteJid", "").replace("@s.whatsapp.net", "")
    if not phone:
        raise HTTPException(status_code=400, detail="phone not found in payload")

    # Extrai texto da mensagem (suporta texto simples e extended text)
    text = (
        message.get("conversation")
        or message.get("extendedTextMessage", {}).get("text")
        or ""
    ).strip()

    if not text:
        return JSONResponse({"status": "ignored", "reason": "no text content"})

    # Recupera histórico da conversa
    history = conversation_store[phone]

    # Processa com o SDR Agent
    result = await process_message(
        phone=phone,
        message=text,
        history=history,
    )

    # Persiste histórico atualizado
    conversation_store[phone] = result["updated_history"]

    # Acumula custo
    cost_store[phone] += result["cost"]["total_usd"]

    return JSONResponse({
        "status":       "processed",
        "category":     result["routing"]["category"],
        "model_used":   result["routing"]["model_to_use"],
        "compacted":    result["compaction"]["compacted"],
        "cost_turn":    result["cost"]["total_usd"],
        "cost_total":   cost_store[phone],
        "savings":      result["cost"]["savings_usd"],
    })


@app.get("/health")
async def health():
    return {"status": "ok", "active_conversations": len(conversation_store)}


@app.get("/evolution-status")
async def evolution_status():
    """
    Valida conectividade com a Evolution API (sem expor credenciais).
    Útil para health check em load balancer / monitoring.
    """
    from integrations.evolution import EvolutionAPIError, EvolutionClient
    try:
        client = EvolutionClient()
        state = await client.check_connection()
        return {
            "ok": state["connected"],
            "state": state["state"],
            "instance": state["instance"],
        }
    except (RuntimeError, EvolutionAPIError) as e:
        raise HTTPException(status_code=503, detail=f"Evolution API check failed: {e}")


@app.get("/cost-report")
async def cost_report():
    """Dashboard básico de custo por lead."""
    return {
        "total_leads":     len(cost_store),
        "total_cost_usd":  round(sum(cost_store.values()), 4),
        "avg_cost_per_lead": round(
            sum(cost_store.values()) / max(len(cost_store), 1), 4
        ),
        "per_lead": dict(sorted(cost_store.items(), key=lambda x: x[1], reverse=True)),
    }


# ── Rodar: uvicorn webhook_server:app --host 0.0.0.0 --port 8000
