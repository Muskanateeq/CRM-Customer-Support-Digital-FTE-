-- TaskNest CRM Database Schema
-- PostgreSQL 17 with pgvector extension
-- Database: neondb
-- Project: CRM-Customer-Support-FTE

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- Table: customers
-- Purpose: Master customer records
-- ============================================
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);

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
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(identifier_type, identifier_value)
);

CREATE INDEX IF NOT EXISTS idx_identifiers_customer ON customer_identifiers(customer_id);
CREATE INDEX IF NOT EXISTS idx_identifiers_value ON customer_identifiers(identifier_value);

-- ============================================
-- Table: conversations
-- Purpose: Track customer conversations across channels
-- ============================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    initial_channel VARCHAR(50) NOT NULL, -- 'email', 'whatsapp', 'web_form'
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'resolved', 'escalated'
    sentiment_score FLOAT, -- 0.0 to 1.0
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversations_customer ON conversations(customer_id);
CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status);
CREATE INDEX IF NOT EXISTS idx_conversations_started ON conversations(started_at DESC);

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
    channel_message_id VARCHAR(255), -- External message ID
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB -- Additional channel-specific data
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_channel_id ON messages(channel_message_id);

-- ============================================
-- Table: tickets
-- Purpose: Support ticket tracking
-- ============================================
CREATE TABLE IF NOT EXISTS tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    conversation_id UUID REFERENCES conversations(id),
    category VARCHAR(100), -- 'general', 'technical', 'billing', etc.
    priority VARCHAR(50) DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    status VARCHAR(50) DEFAULT 'open', -- 'open', 'processing', 'resolved', 'escalated'
    source_channel VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    resolution_notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_tickets_customer ON tickets(customer_id);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_created ON tickets(created_at DESC);

-- ============================================
-- Table: knowledge_base
-- Purpose: Product documentation with vector embeddings
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    embedding vector(1536), -- OpenAI text-embedding-3-small
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON knowledge_base
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category);

-- ============================================
-- Trigger: Update updated_at timestamp
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Sample Data: Insert product documentation into knowledge_base
-- (Will be populated with embeddings in Phase 2)
-- ============================================

-- Note: Embeddings will be generated using OpenAI API and inserted separately
-- For now, we create the structure

COMMENT ON TABLE customers IS 'Master customer records with email and phone';
COMMENT ON TABLE customer_identifiers IS 'Multiple identifiers (email, phone, WhatsApp) linked to single customer';
COMMENT ON TABLE conversations IS 'Customer conversations across all channels';
COMMENT ON TABLE messages IS 'All messages (inbound/outbound) with channel info';
COMMENT ON TABLE tickets IS 'Support tickets for tracking and escalation';
COMMENT ON TABLE knowledge_base IS 'Product documentation with vector embeddings for semantic search';
