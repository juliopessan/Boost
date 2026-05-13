import hashlib
import hmac
import structlog

log = structlog.get_logger()


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def hash_phone(phone: str) -> str:
    return hashlib.sha256(phone.encode()).hexdigest()


def extract_messages(body: dict) -> list[dict]:
    messages = []
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                messages.append({
                    "message": msg,
                    "contacts": value.get("contacts", []),
                    "metadata": value.get("metadata", {}),
                    "business_account_id": entry.get("id", ""),
                })
    return messages
