"""
AWS Lambda handler — SQS consumer that routes WhatsApp messages to the correct handler.
"""
import json
import os
import time
import structlog
import logging

from workers.handlers.audio_handler import AudioHandler
from workers.handlers.button_handler import ButtonHandler
from workers.handlers.fallback_handler import FallbackHandler
from workers.handlers.text_handler import TextHandler
from workers.services.database import DatabaseService
from workers.services.session import SessionService
from workers.services.whatsapp_sender import WhatsAppSender

logging.basicConfig(level=logging.INFO)
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)
log = structlog.get_logger()


def _build_dependencies():
    session = SessionService(redis_url=os.environ["REDIS_URL"])
    sender = WhatsAppSender(
        phone_number_id=os.environ["WHATSAPP_PHONE_NUMBER_ID"],
        access_token=os.environ["WHATSAPP_ACCESS_TOKEN"],
    )
    db = DatabaseService(dsn=os.environ["DATABASE_URL"])
    return session, sender, db


def _route(envelope: dict, session: SessionService, sender: WhatsAppSender) -> dict:
    msg_type = envelope.get("type", "unknown")

    handlers = {
        "text": lambda: TextHandler(session, sender).handle(envelope),
        "button": lambda: ButtonHandler(session, sender).handle(envelope),
        "interactive": lambda: ButtonHandler(session, sender).handle(envelope),
        "audio": lambda: AudioHandler(sender).handle(envelope),
    }

    handler_fn = handlers.get(msg_type, lambda: FallbackHandler(sender).handle(envelope))
    return handler_fn()


def handler(event: dict, context) -> dict:
    session, sender, db = _build_dependencies()
    results = []

    for record in event.get("Records", []):
        start_ms = int(time.time() * 1000)
        envelope = {}
        message_id = "unknown"

        try:
            envelope = json.loads(record["body"])
            message_id = envelope.get("message_id", "unknown")
            phone_hash = envelope.get("phone_hash", "unknown")

            log.info("router.processing", message_id=message_id, type=envelope.get("type"))

            result = _route(envelope, session, sender)
            latency_ms = int(time.time() * 1000) - start_ms

            db.save_message(
                message_id=message_id,
                flow_id="default",
                phone_hash=phone_hash,
                msg_type=envelope.get("type", "unknown"),
                status="success",
                latency_ms=latency_ms,
            )

            log.info("router.success", message_id=message_id, latency_ms=latency_ms)
            results.append({"message_id": message_id, "status": "success"})

        except Exception as e:
            log.error("router.error", message_id=message_id, error=str(e))
            db.save_dlq_entry(message_id, envelope, str(e))
            db.save_message(
                message_id=message_id,
                flow_id="default",
                phone_hash=envelope.get("phone_hash", "unknown"),
                msg_type=envelope.get("type", "unknown"),
                status="error",
                error_reason=str(e),
            )
            results.append({"message_id": message_id, "status": "error", "error": str(e)})

    db.close()
    return {"processed": len(results), "results": results}
