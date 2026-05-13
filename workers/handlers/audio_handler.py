import structlog
from workers.services.whatsapp_sender import WhatsAppSender

log = structlog.get_logger()


class AudioHandler:
    def __init__(self, sender: WhatsAppSender):
        self.sender = sender

    def handle(self, envelope: dict) -> dict:
        phone = envelope["phone"]
        phone_hash = envelope["phone_hash"]
        message_id = envelope["message_id"]

        log.info("audio_handler.processing", phone_hash=phone_hash)

        self.sender.send_text(
            phone,
            "Recebi seu áudio! 🎤 No momento não consigo processar mensagens de voz.\n"
            "Por favor, envie sua mensagem em texto. Digite *oi* para recomeçar.",
        )

        return {"handled": True, "action": "audio_not_supported"}
