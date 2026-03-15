-- ============================================
-- TaskNest CRM Database Schema
-- PostgreSQL 17 with pgvector extension
-- Database: neondb
-- Project: CRM-Customer-Support-FTE
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm; -- For text similarity search

-- ============================================
-- Table: customers
-- Purpose: Master customer records
-- ============================================
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_created ON customers(created_at DESC);

COMMENT ON TABLE customers IS 'Master customer records with email and phone';
COMMENT ON COLUMN customers.metadata IS 'Additional customer data (preferences, tags, etc.)';

-- ============================================
-- Table: customer_identifiers
-- Purpose: Link multiple identifiers to single customer
-- ============================================
CREATE TABLE IF NOT EXISTS customer_identifiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    identifier_type VARCHAR(50) NOT NULL, -- 'email', 'whatsapp', 'phone'
    identifier_value VARCHAR(255) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(identifier_type, identifier_value)
);

CREATE INDEX IF NOT EXISTS idx_identifiers_customer ON customer_identifiers(customer_id);
CREATE INDEX IF NOT EXISTS idx_identifiers_value ON customer_identifiers(identifier_value);
CREATE INDEX IF NOT EXISTS idx_identifiers_type ON customer_identifiers(identifier_type);

COMMENT ON TABLE customer_identifiers IS 'Multiple identifiers (email, phone, WhatsApp) linked to single customer for cross-channel tracking';

-- ============================================
-- Table: conversations
-- Purpose: Track customer conversations across channels
-- ============================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    initial_channel VARCHAR(50) NOT NULL, -- 'email', 'whatsapp', 'web_form'
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'resolved', 'escalated'
    sentiment_score FLOAT CHECK (sentiment_score >= 0 AND sentiment_score <= 1), -- 0.0 to 1.0
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    resolution_type VARCHAR(50), -- 'resolved', 'escalated', 'abandoned'
    escalated_to VARCHAR(255), -- Human agent name/email
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_conversations_customer ON conversations(customer_id);
CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status);
CREATE INDEX IF NOT EXISTS idx_conversations_started ON conversations(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_active ON conversations(status) WHERE status = 'active';

COMMENT ON TABLE conversations IS 'Customer conversations across all channels with sentiment tracking';

-- ============================================
-- Table: messages
-- Purpose: Store all messages (inbound/outbound)
-- ============================================
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'customer', 'agent', 'system'
    content TEXT NOT NULL,
    channel VARCHAR(50) NOT NULL, -- 'email', 'whatsapp', 'web_form'
    direction VARCHAR(50) NOT NULL, -- 'inbound', 'outbound'
    channel_message_id VARCHAR(255), -- External message ID (Gmail ID, Twilio SID, etc.)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_used INTEGER, -- AI tokens consumed
    latency_ms INTEGER, -- Response time in milliseconds
    tool_calls JSONB DEFAULT '[]', -- Tools used by agent
    delivery_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'sent', 'delivered', 'failed'
    metadata JSONB DEFAULT '{}' -- Additional channel-specific data
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_channel_id ON messages(channel_message_id);
CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);

COMMENT ON TABLE messages IS 'All messages (inbound/outbound) with channel info and AI metrics';

-- ============================================
-- Table: tickets
-- Purpose: Support ticket tracking
-- ============================================
CREATE TABLE IF NOT EXISTS tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    category VARCHAR(100), -- 'general', 'technical', 'billing', 'account', 'feature_request'
    priority VARCHAR(50) DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    status VARCHAR(50) DEFAULT 'open', -- 'open', 'processing', 'resolved', 'escalated', 'closed'
    source_channel VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    assigned_to VARCHAR(255), -- Human agent assigned
    sla_deadline TIMESTAMP WITH TIME ZONE, -- SLA deadline for response
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_tickets_customer ON tickets(customer_id);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_created ON tickets(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority);
CREATE INDEX IF NOT EXISTS idx_tickets_open ON tickets(status) WHERE status IN ('open', 'processing');

COMMENT ON TABLE tickets IS 'Support tickets for tracking and escalation with SLA management';

-- ============================================
-- Table: knowledge_base
-- Purpose: Product documentation with vector embeddings
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    source VARCHAR(255), -- 'product_docs', 'company_profile', 'faq', etc.
    embedding vector(1536), -- OpenAI text-embedding-3-small (1536 dimensions)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Vector similarity index for semantic search
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON knowledge_base
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Text search indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_title_trgm ON knowledge_base USING gin(title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_knowledge_content_trgm ON knowledge_base USING gin(content gin_trgm_ops);

COMMENT ON TABLE knowledge_base IS 'Product documentation with vector embeddings for semantic search';

-- ============================================
-- Table: agent_metrics
-- Purpose: Track AI agent performance metrics
-- ============================================
CREATE TABLE IF NOT EXISTS agent_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    model_used VARCHAR(100), -- 'gpt-4o', 'llama-3.3-70b', etc.
    tokens_prompt INTEGER,
    tokens_completion INTEGER,
    tokens_total INTEGER,
    latency_ms INTEGER,
    tools_used JSONB DEFAULT '[]',
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_metrics_conversation ON agent_metrics(conversation_id);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_created ON agent_metrics(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_model ON agent_metrics(model_used);

COMMENT ON TABLE agent_metrics IS 'AI agent performance metrics for monitoring and optimization';

-- ============================================
-- Table: channel_configs
-- Purpose: Channel-specific configuration
-- ============================================
CREATE TABLE IF NOT EXISTS channel_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel VARCHAR(50) UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    config JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE channel_configs IS 'Channel-specific configuration (email, WhatsApp, web form)';

-- ============================================
-- Triggers: Auto-update timestamps
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_base_updated_at
    BEFORE UPDATE ON knowledge_base
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_channel_configs_updated_at
    BEFORE UPDATE ON channel_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Views: Useful queries
-- ============================================

-- Active conversations with customer info
CREATE OR REPLACE VIEW active_conversations_view AS
SELECT
    c.id as conversation_id,
    c.customer_id,
    cu.name as customer_name,
    cu.email as customer_email,
    c.initial_channel,
    c.status,
    c.sentiment_score,
    c.started_at,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message_at
FROM conversations c
JOIN customers cu ON c.customer_id = cu.id
LEFT JOIN messages m ON m.conversation_id = c.id
WHERE c.status = 'active'
GROUP BY c.id, c.customer_id, cu.name, cu.email, c.initial_channel, c.status, c.sentiment_score, c.started_at;

-- Open tickets summary
CREATE OR REPLACE VIEW open_tickets_view AS
SELECT
    t.id as ticket_id,
    t.customer_id,
    cu.name as customer_name,
    cu.email as customer_email,
    t.category,
    t.priority,
    t.status,
    t.source_channel,
    t.created_at,
    t.sla_deadline,
    CASE
        WHEN t.sla_deadline < NOW() THEN 'overdue'
        WHEN t.sla_deadline < NOW() + INTERVAL '2 hours' THEN 'urgent'
        ELSE 'on_time'
    END as sla_status
FROM tickets t
JOIN customers cu ON t.customer_id = cu.id
WHERE t.status IN ('open', 'processing', 'escalated');

-- ============================================
-- Initial Data: Channel Configurations
-- ============================================
INSERT INTO channel_configs (channel, enabled, config) VALUES
('email', true, '{"max_length": 2000, "polling_interval": 30, "auto_reply": true}'::jsonb),
('whatsapp', true, '{"max_length": 1600, "media_support": true, "auto_reply": true}'::jsonb),
('web_form', true, '{"max_length": 1000, "streaming": true, "auto_reply": true}'::jsonb)
ON CONFLICT (channel) DO NOTHING;

-- ============================================
-- Database Setup Complete
-- ============================================
-- Run this script with: psql $DATABASE_URL -f schema.sql
-- Or use the setup_database.sh script
