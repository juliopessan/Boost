import structlog
from workers.services.session import SessionService
from workers.services.whatsapp_sender import WhatsAppSender

log = structlog.get_logger()


class ButtonHandler:
    def __init__(self, session: SessionService, sender: WhatsAppSender):
        self.session = session
        self.sender = sender

    def handle(self, envelope: dict) -> dict:
        phone = envelope["phone"]
        phone_hash = envelope["phone_hash"]
        message_id = envelope["message_id"]

        payload = envelope["payload"]
        button_id = payload.get("button", {}).get("payload", "")
        button_text = payload.get("button", {}).get("text", "")

        state = self.session.get(phone_hash)

        log.info("button_handler.processing", phone_hash=phone_hash, button_id=button_id)
        self.sender.mark_read(message_id)

        if button_id.startswith("confirm_order_"):
            order_id = button_id.replace("confirm_order_", "")
            self.sender.send_text(phone, f"✅ Pedido #{order_id} confirmado!\nVocê receberá atualizações aqui.")
            self.session.delete(phone_hash)
            return {"handled": True, "action": "order_confirmed", "order_id": order_id}

        if button_id == "cancel_order":
            self.sender.send_text(phone, "Pedido cancelado. Digite *oi* para recomeçar.")
            self.session.delete(phone_hash)
            return {"handled": True, "action": "order_cancelled"}

        self.sender.send_text(phone, "Opção não reconhecida. Digite *oi* para recomeçar.")
        return {"handled": False, "button_id": button_id}
