import structlog
from workers.services.whatsapp_sender import WhatsAppSender

log = structlog.get_logger()


class FallbackHandler:
    def __init__(self, sender: WhatsAppSender):
        self.sender = sender

    def handle(self, envelope: dict) -> dict:
        phone = envelope["phone"]
        phone_hash = envelope["phone_hash"]
        msg_type = envelope["type"]

        log.info("fallback_handler.processing", phone_hash=phone_hash, type=msg_type)

        self.sender.send_text(
            phone,
            "Olá! No momento não consigo processar esse tipo de mensagem. 😅\n"
            "Digite *oi* para ver o menu principal.",
        )

        return {"handled": False, "original_type": msg_type}
