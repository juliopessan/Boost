import uuid
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Response

from webhook.models.messages import MessageType, SQSEnvelope
from webhook.services.sqs import SQSService
from webhook.services.whatsapp import extract_messages, hash_phone, verify_signature

log = structlog.get_logger()
router = APIRouter()


def _get_message_type(raw: str) -> MessageType:
    try:
        return MessageType(raw)
    except ValueError:
        return MessageType.UNKNOWN


async def _enqueue_messages(body: dict, sqs: SQSService) -> None:
    for item in extract_messages(body):
        msg = item["message"]
        metadata = item["metadata"]
        phone = msg.get("from", "")

        envelope = SQSEnvelope(
            message_id=msg.get("id", str(uuid.uuid4())),
            phone=phone,
            phone_hash=hash_phone(phone),
            type=_get_message_type(msg.get("type", "unknown")),
            payload=msg,
            received_at=datetime.now(timezone.utc).isoformat(),
            business_account_id=item["business_account_id"],
            display_phone_number=metadata.get("display_phone_number", ""),
        )

        sqs.publish(envelope.model_dump(), deduplication_id=envelope.message_id)
        log.info("webhook.message_enqueued", phone_hash=envelope.phone_hash, type=envelope.type)


@router.get("/webhook")
async def verify_webhook(request: Request):
    """WhatsApp webhook verification challenge."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    verify_token = request.app.state.settings.WHATSAPP_VERIFY_TOKEN

    if mode == "subscribe" and token == verify_token:
        log.info("webhook.verified")
        return Response(content=challenge, media_type="text/plain")

    raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """Receive WhatsApp messages and enqueue to SQS."""
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    settings = request.app.state.settings
    if not verify_signature(raw_body, signature, settings.WHATSAPP_APP_SECRET):
        log.warning("webhook.invalid_signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    body = await request.json()

    if body.get("object") != "whatsapp_business_account":
        return {"status": "ignored"}

    background_tasks.add_task(_enqueue_messages, body, request.app.state.sqs)
    return {"status": "ok"}
