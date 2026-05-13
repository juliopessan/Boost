-- Boost Database Schema
-- PostgreSQL 15+

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Flows: definições de automação
CREATE TABLE flows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    trigger_type TEXT NOT NULL CHECK (trigger_type IN ('text','button','interactive','audio','image','video','document','order','fallback')),
    handler_arn TEXT NOT NULL DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT false,
    timeout_minutes INTEGER NOT NULL DEFAULT 30,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Messages: histórico de mensagens processadas
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    flow_id TEXT NOT NULL DEFAULT 'default',
    phone_hash TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('queued','processing','success','error','dlq')),
    latency_ms INTEGER,
    error_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_status ON messages(status);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_messages_phone_hash ON messages(phone_hash);

-- DLQ: mensagens que falharam repetidamente
CREATE TABLE dlq_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id TEXT UNIQUE NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}',
    retry_count INTEGER NOT NULL DEFAULT 1,
    last_error TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Settings: configurações da plataforma
CREATE TABLE settings (
    id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1), -- singleton
    dlq_alert_threshold INTEGER NOT NULL DEFAULT 10,
    default_session_timeout INTEGER NOT NULL DEFAULT 30,
    notification_email TEXT NOT NULL DEFAULT '',
    slack_webhook_url TEXT NOT NULL DEFAULT ''
);

INSERT INTO settings DEFAULT VALUES ON CONFLICT DO NOTHING;

-- Função para métricas horárias (usada pelo dashboard)
CREATE OR REPLACE FUNCTION get_hourly_metrics()
RETURNS TABLE (hour TEXT, success BIGINT, error BIGINT, total BIGINT)
LANGUAGE SQL AS $$
    SELECT
        TO_CHAR(DATE_TRUNC('hour', created_at), 'HH24:MI') AS hour,
        COUNT(*) FILTER (WHERE status = 'success') AS success,
        COUNT(*) FILTER (WHERE status = 'error') AS error,
        COUNT(*) AS total
    FROM messages
    WHERE created_at >= NOW() - INTERVAL '24 hours'
    GROUP BY DATE_TRUNC('hour', created_at)
    ORDER BY DATE_TRUNC('hour', created_at);
$$;

-- Dados iniciais: flows de exemplo
INSERT INTO flows (name, trigger_type, is_active, timeout_minutes) VALUES
    ('Menu Principal', 'text', true, 30),
    ('Resposta a Botão', 'button', true, 10),
    ('Interativo', 'interactive', true, 10),
    ('Fallback Geral', 'fallback', true, 5);
