import structlog
from workers.services.session import SessionService
from workers.services.whatsapp_sender import WhatsAppSender

log = structlog.get_logger()


class TextHandler:
    def __init__(self, session: SessionService, sender: WhatsAppSender):
        self.session = session
        self.sender = sender

    def handle(self, envelope: dict) -> dict:
        phone = envelope["phone"]
        phone_hash = envelope["phone_hash"]
        message_id = envelope["message_id"]
        body = envelope["payload"].get("text", {}).get("body", "").strip().lower()

        state = self.session.get(phone_hash)
        current_step = state.get("step", "initial")

        log.info("text_handler.processing", phone_hash=phone_hash, step=current_step)

        self.sender.mark_read(message_id)

        if current_step == "initial":
            return self._handle_initial(phone, phone_hash, body, state)

        if current_step == "awaiting_name":
            return self._handle_awaiting_name(phone, phone_hash, body, state)

        return self._handle_fallback(phone, phone_hash)

    def _handle_initial(self, phone: str, phone_hash: str, body: str, state: dict) -> dict:
        greetings = {"oi", "olá", "ola", "hi", "hello", "hey", "início", "inicio", "start"}

        if body in greetings or not state:
            self.sender.send_text(
                phone,
                "Olá! Bem-vindo ao Boost 👋\nComo posso te ajudar hoje?\n\n"
                "Digite *1* para fazer um pedido\n"
                "Digite *2* para acompanhar um pedido\n"
                "Digite *3* para falar com atendimento",
            )
            self.session.update(phone_hash, {"step": "main_menu"})
            return {"handled": True, "next_step": "main_menu"}

        return self._handle_main_menu(phone, phone_hash, body, state)

    def _handle_main_menu(self, phone: str, phone_hash: str, body: str, state: dict) -> dict:
        if body == "1":
            self.sender.send_text(phone, "Qual é o seu nome?")
            self.session.update(phone_hash, {"step": "awaiting_name"})
            return {"handled": True, "next_step": "awaiting_name"}

        if body == "2":
            self.sender.send_text(phone, "Por favor, informe o número do seu pedido:")
            self.session.update(phone_hash, {"step": "awaiting_order_id"})
            return {"handled": True, "next_step": "awaiting_order_id"}

        if body == "3":
            self.sender.send_text(phone, "Aguarde, um atendente entrará em contato em breve! ✅")
            self.session.delete(phone_hash)
            return {"handled": True, "next_step": "transferred"}

        return self._handle_fallback(phone, phone_hash)

    def _handle_awaiting_name(self, phone: str, phone_hash: str, body: str, state: dict) -> dict:
        name = body.title()
        self.sender.send_text(
            phone,
            f"Prazer, {name}! 😊\nQual produto você deseja pedir?",
        )
        self.session.update(phone_hash, {"step": "awaiting_product", "name": name})
        return {"handled": True, "next_step": "awaiting_product"}

    def _handle_fallback(self, phone: str, phone_hash: str) -> dict:
        self.sender.send_text(
            phone,
            "Não entendi sua mensagem. Digite *oi* para recomeçar.",
        )
        return {"handled": False, "next_step": "fallback"}
