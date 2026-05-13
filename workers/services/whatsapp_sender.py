import httpx
import structlog

log = structlog.get_logger()

WHATSAPP_API_URL = "https://graph.facebook.com/v19.0/{phone_number_id}/messages"


class WhatsAppSender:
    def __init__(self, phone_number_id: str, access_token: str):
        self.url = WHATSAPP_API_URL.format(phone_number_id=phone_number_id)
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def _post(self, payload: dict) -> dict:
        with httpx.Client(timeout=10) as client:
            response = client.post(self.url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def send_text(self, to: str, body: str) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": body},
        }
        result = self._post(payload)
        log.info("whatsapp.text_sent", to_hash=to[-4:], message_id=result.get("messages", [{}])[0].get("id"))
        return result

    def send_buttons(self, to: str, body: str, buttons: list[dict]) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": b["id"], "title": b["title"]}}
                        for b in buttons
                    ]
                },
            },
        }
        result = self._post(payload)
        log.info("whatsapp.buttons_sent", to_hash=to[-4:])
        return result

    def send_list(self, to: str, body: str, button_text: str, sections: list[dict]) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": body},
                "action": {"button": button_text, "sections": sections},
            },
        }
        result = self._post(payload)
        log.info("whatsapp.list_sent", to_hash=to[-4:])
        return result

    def mark_read(self, message_id: str) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        return self._post(payload)
