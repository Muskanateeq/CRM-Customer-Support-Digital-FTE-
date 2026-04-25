-- Admin Portal Schema Migration
-- Adds tables and fields for human agent support system
-- Date: 2026-04-24

-- ============================================
-- Table: admin_users
-- Purpose: Admin/support team authentication
-- ============================================
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'admin', -- 'admin', 'agent', 'viewer' (future use)
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_admin_users_email ON admin_users(email);
CREATE INDEX IF NOT EXISTS idx_admin_users_active ON admin_users(is_active);

COMMENT ON TABLE admin_users IS 'Admin and support team members who handle escalated tickets';

-- ============================================
-- Table: ticket_responses
-- Purpose: Track human responses to tickets
-- ============================================
CREATE TABLE IF NOT EXISTS ticket_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    admin_user_id UUID NOT NULL REFERENCES admin_users(id),
    content TEXT NOT NULL,
    sent_via_channel VARCHAR(50) NOT NULL, -- 'email', 'whatsapp', 'web_form'
    sent_at TIMESTAMP DEFAULT NOW(),
    delivery_status VARCHAR(50) DEFAULT 'sent', -- 'sent', 'delivered', 'failed'
    metadata JSONB -- Channel-specific delivery info
);

CREATE INDEX IF NOT EXISTS idx_ticket_responses_ticket ON ticket_responses(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_responses_admin ON ticket_responses(admin_user_id);
CREATE INDEX IF NOT EXISTS idx_ticket_responses_sent ON ticket_responses(sent_at DESC);

COMMENT ON TABLE ticket_responses IS 'Human agent responses sent to customers via admin portal';

-- ============================================
-- Table: ticket_notes
-- Purpose: Internal notes for admin team (not visible to customers)
-- ============================================
CREATE TABLE IF NOT EXISTS ticket_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    admin_user_id UUID NOT NULL REFERENCES admin_users(id),
    note_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ticket_notes_ticket ON ticket_notes(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_notes_created ON ticket_notes(created_at DESC);

COMMENT ON TABLE ticket_notes IS 'Private internal notes for admin team, not visible to customers';

-- ============================================
-- Update tickets table with escalation fields
-- ============================================
ALTER TABLE tickets
    ADD COLUMN IF NOT EXISTS assigned_to UUID REFERENCES admin_users(id),
    ADD COLUMN IF NOT EXISTS last_human_response_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS escalation_reason TEXT,
    ADD COLUMN IF NOT EXISTS escalated_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_tickets_assigned ON tickets(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tickets_escalated ON tickets(escalated_at DESC);

-- ============================================
-- Update admin_users trigger for updated_at
-- ============================================
CREATE TRIGGER update_admin_users_updated_at BEFORE UPDATE ON admin_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Insert default admin user
-- Password: Admin@123 (hashed with bcrypt)
-- IMPORTANT: Change this password after first login!
-- ============================================
INSERT INTO admin_users (email, password_hash, name, role)
VALUES (
    'custora.admin.support@gmail.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztJ.nE8QLqjG', -- Admin@123
    'Custora Admin',
    'admin'
)
ON CONFLICT (email) DO NOTHING;

COMMENT ON COLUMN tickets.assigned_to IS 'Admin user assigned to handle this escalated ticket';
COMMENT ON COLUMN tickets.last_human_response_at IS 'Timestamp of last human response sent';
COMMENT ON COLUMN tickets.escalation_reason IS 'Reason why ticket was escalated to human';
COMMENT ON COLUMN tickets.escalated_at IS 'Timestamp when ticket was escalated';
