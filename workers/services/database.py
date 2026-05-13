import json
import psycopg2
import psycopg2.extras
import structlog

log = structlog.get_logger()


class DatabaseService:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self._conn = None

    @property
    def conn(self):
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(self.dsn)
            self._conn.autocommit = False
        return self._conn

    def save_message(self, message_id: str, flow_id: str, phone_hash: str,
                     msg_type: str, status: str, latency_ms: int | None = None,
                     error_reason: str | None = None) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO messages (id, flow_id, phone_hash, type, status, latency_ms, error_reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET status = EXCLUDED.status,
                    latency_ms = EXCLUDED.latency_ms,
                    error_reason = EXCLUDED.error_reason
                """,
                (message_id, flow_id, phone_hash, msg_type, status, latency_ms, error_reason),
            )
        self.conn.commit()
        log.debug("db.message_saved", message_id=message_id, status=status)

    def get_flow_by_trigger(self, trigger_type: str) -> dict | None:
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM flows WHERE trigger_type = %s AND is_active = true LIMIT 1",
                (trigger_type,),
            )
            row = cur.fetchone()
        return dict(row) if row else None

    def save_dlq_entry(self, message_id: str, payload: dict, error: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dlq_entries (message_id, payload, last_error, retry_count)
                VALUES (%s, %s, %s, 1)
                ON CONFLICT (message_id) DO UPDATE
                SET retry_count = dlq_entries.retry_count + 1,
                    last_error = EXCLUDED.last_error
                """,
                (message_id, json.dumps(payload), error),
            )
        self.conn.commit()
        log.warning("db.dlq_entry_saved", message_id=message_id)

    def close(self) -> None:
        if self._conn and not self._conn.closed:
            self._conn.close()
