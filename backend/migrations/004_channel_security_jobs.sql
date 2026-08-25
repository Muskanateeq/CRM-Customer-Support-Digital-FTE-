-- Secure, durable inbound processing for Gmail and WhatsApp.

CREATE TABLE IF NOT EXISTS channel_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel VARCHAR(50) NOT NULL CHECK (channel IN ('email', 'whatsapp')),
    external_message_id VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    max_attempts INTEGER NOT NULL DEFAULT 5 CHECK (max_attempts > 0),
    available_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    locked_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    last_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (channel, external_message_id)
);

CREATE INDEX IF NOT EXISTS idx_channel_jobs_claim
    ON channel_jobs (status, available_at, created_at)
    WHERE status IN ('pending', 'processing');

COMMENT ON TABLE channel_jobs IS
    'Durable, idempotent inbound Gmail and WhatsApp processing queue';
