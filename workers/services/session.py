import json
import redis
import structlog

log = structlog.get_logger()


class SessionService:
    def __init__(self, redis_url: str, default_ttl: int = 1800):
        self.client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = default_ttl

    def _key(self, phone_hash: str) -> str:
        return f"session:{phone_hash}"

    def get(self, phone_hash: str) -> dict:
        raw = self.client.get(self._key(phone_hash))
        if not raw:
            return {}
        return json.loads(raw)

    def set(self, phone_hash: str, state: dict, ttl: int | None = None) -> None:
        self.client.setex(
            self._key(phone_hash),
            ttl or self.default_ttl,
            json.dumps(state),
        )
        log.debug("session.updated", phone_hash=phone_hash)

    def delete(self, phone_hash: str) -> None:
        self.client.delete(self._key(phone_hash))
        log.info("session.deleted", phone_hash=phone_hash)

    def update(self, phone_hash: str, updates: dict, ttl: int | None = None) -> dict:
        state = self.get(phone_hash)
        state.update(updates)
        self.set(phone_hash, state, ttl)
        return state
