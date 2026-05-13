from enum import Enum
from typing import Any
from pydantic import BaseModel


class MessageType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    BUTTON = "button"
    INTERACTIVE = "interactive"
    ORDER = "order"
    UNKNOWN = "unknown"


class WhatsAppContact(BaseModel):
    wa_id: str
    profile: dict[str, Any] = {}


class WhatsAppMessage(BaseModel):
    id: str
    from_: str
    timestamp: str
    type: MessageType
    text: dict[str, Any] | None = None
    audio: dict[str, Any] | None = None
    image: dict[str, Any] | None = None
    video: dict[str, Any] | None = None
    document: dict[str, Any] | None = None
    button: dict[str, Any] | None = None
    interactive: dict[str, Any] | None = None
    order: dict[str, Any] | None = None

    class Config:
        populate_by_name = True
        fields = {"from_": "from"}


class SQSEnvelope(BaseModel):
    message_id: str
    phone: str
    phone_hash: str
    type: MessageType
    payload: dict[str, Any]
    received_at: str
    business_account_id: str
    display_phone_number: str
