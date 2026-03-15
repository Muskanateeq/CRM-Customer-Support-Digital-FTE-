# TaskNest Customer Success FTE - Technical Specification

## Document Information

**Project:** TaskNest Customer Success AI Agent (Digital FTE)
**Version:** 1.0
**Date:** February 25, 2026
**Status:** Approved for Implementation
**Phase:** Transitioning from Incubation to Specialization

---

## 1. Executive Summary

### 1.1 Purpose
Build a production-ready AI Customer Success Agent (Digital FTE) that handles customer inquiries 24/7 across three channels: Email (Gmail), WhatsApp (Twilio), and Web Support Form.

### 1.2 Success Criteria
- **Resolution Rate:** >70% of queries resolved without human intervention
- **Response Time:** <3 seconds P95 latency
- **Escalation Rate:** <25% of conversations escalated to humans
- **Uptime:** 99.9% availability
- **Customer Satisfaction:** >4.0/5.0 rating

### 1.3 Scope
**In Scope:**
- Multi-channel support (Email, WhatsApp, Web Form)
- Knowledge base search and response generation
- Ticket creation and management
- Smart escalation to human agents
- Cross-channel customer identification
- Sentiment analysis
- Channel-appropriate response formatting

**Out of Scope:**
- Voice/phone support
- Video chat support
- Social media monitoring
- Payment processing
- External CRM integration (PostgreSQL IS the CRM)

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CUSTOMER CHANNELS                         │
│         [Gmail] [WhatsApp] [Web Form]                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI GATEWAY                             │
│  /webhooks/gmail  /webhooks/whatsapp  /support/submit       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   KAFKA EVENT BUS                            │
│  Topics: tickets.incoming, email.inbound, whatsapp.inbound  │
│          escalations, metrics, dlq                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              MESSAGE PROCESSOR WORKERS                       │
│  - Customer Resolution                                       │
│  - Conversation Management                                   │
│  - OpenAI Agent Execution                                    │
│  - Response Routing                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│      OPENAI AGENT (GPT-4o) with 5 Tools                     │
│  1. search_knowledge_base                                    │
│  2. create_ticket                                            │
│  3. get_customer_history                                     │
│  4. escalate_to_human                                        │
│  5. send_response                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 NEON POSTGRESQL CRM                          │
│  Tables: customers, conversations, messages, tickets,        │
│          knowledge_base, customer_identifiers                │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (async REST API)
- OpenAI Agents SDK (agent implementation)
- Neon PostgreSQL (serverless, with pgvector)
- Apache Kafka (aiokafka for event streaming)
- asyncpg (async database driver)

**Frontend:**
- Next.js 14.2.x (App Router)
- React 18
- TypeScript
- TailwindCSS

**Integrations:**
- Gmail API (OAuth 2.0 + Google Pub/Sub)
- Twilio WhatsApp API
- OpenAI API (GPT-4o)

**Infrastructure:**
- Docker (containerization)
- Kubernetes (orchestration)

---

## 3. Database Schema

### 3.1 Entity Relationship Diagram

```
customers (1) ──< (M) customer_identifiers
    │
    │ (1)
    │
    ├──< (M) conversations
    │         │
    │         │ (1)
    │         │
    │         └──< (M) messages
    │
    └──< (M) tickets

knowledge_base (standalone)
```

### 3.2 Table Definitions

#### 3.2.1 customers
```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone);
```

#### 3.2.2 customer_identifiers
```sql
CREATE TABLE customer_identifiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    identifier_type VARCHAR(50) NOT NULL, -- 'email', 'whatsapp', 'phone'
    identifier_value VARCHAR(255) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(identifier_type, identifier_value)
);

CREATE INDEX idx_identifiers_customer ON customer_identifiers(customer_id);
CREATE INDEX idx_identifiers_value ON customer_identifiers(identifier_value);
```

#### 3.2.3 conversations
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    initial_channel VARCHAR(50) NOT NULL, -- 'email', 'whatsapp', 'web_form'
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'resolved', 'escalated'
    sentiment_score FLOAT, -- 0.0 to 1.0
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP
);

CREATE INDEX idx_conversations_customer ON conversations(customer_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_started ON conversations(started_at DESC);
```

#### 3.2.4 messages
```sql
CREATE TABLE messages (
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

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created ON messages(created_at DESC);
CREATE INDEX idx_messages_channel_id ON messages(channel_message_id);
```

#### 3.2.5 tickets
```sql
CREATE TABLE tickets (
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

CREATE INDEX idx_tickets_customer ON tickets(customer_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_created ON tickets(created_at DESC);
```

#### 3.2.6 knowledge_base
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    embedding vector(1536), -- OpenAI text-embedding-3-small
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_knowledge_embedding ON knowledge_base
    USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_knowledge_category ON knowledge_base(category);
```

---

## 4. OpenAI Agent Specification

### 4.1 Agent Configuration

```python
agent = Agent(
    name="Customer Success FTE",
    model="gpt-4o",
    temperature=0.7,
    instructions="[See section 4.2]",
    tools=[
        search_knowledge_base,
        create_ticket,
        get_customer_history,
        escalate_to_human,
        send_response
    ]
)
```

### 4.2 System Instructions

```
You are a Customer Success agent for TaskNest, a project management SaaS platform.

## Your Purpose
Handle routine customer support queries with speed, accuracy, and empathy across multiple channels.

## Channel Awareness
You receive messages from three channels. Adapt your communication style:
- **Email**: Formal, detailed responses. Include proper greeting and signature.
- **WhatsApp**: Concise, conversational. Keep responses under 300 characters when possible.
- **Web Form**: Semi-formal, helpful. Balance detail with readability.

## Core Behaviors
1. ALWAYS create a ticket at conversation start (include channel!)
2. Check customer history ACROSS ALL CHANNELS before responding
3. Search knowledge base before answering product questions
4. Be concise on WhatsApp, detailed on email
5. Monitor sentiment - escalate if customer becomes frustrated

## Hard Constraints
- NEVER discuss pricing - escalate immediately
- NEVER promise features not in documentation
- NEVER process refunds - escalate to billing
- NEVER share internal processes or systems
- ALWAYS use send_response tool to reply (ensures proper channel formatting)

## Escalation Triggers
- Customer mentions "lawyer", "legal", or "sue"
- Customer uses profanity or aggressive language
- You cannot find relevant information after 2 searches
- Customer explicitly requests human help
- WhatsApp: customer sends 'human' or 'agent'

## Cross-Channel Continuity
If a customer has contacted us before (any channel), acknowledge it:
"I see you contacted us previously about X. Let me help you further..."
```

### 4.3 Tool Definitions

#### 4.3.1 search_knowledge_base

```python
class KnowledgeSearchInput(BaseModel):
    query: str
    max_results: int = 5

@function_tool
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    """Search product documentation for relevant information.

    Use this when the customer asks questions about product features,
    how to use something, or needs technical information.
    """
    # Implementation: Vector similarity search using pgvector
    # Returns: Formatted search results with relevance scores
```

#### 4.3.2 create_ticket

```python
class TicketInput(BaseModel):
    customer_id: str
    issue: str
    priority: str = "medium"
    category: Optional[str] = None
    channel: Channel  # Enum: email, whatsapp, web_form

@function_tool
async def create_ticket(input: TicketInput) -> str:
    """Create a support ticket for tracking.

    ALWAYS create a ticket at the start of every conversation.
    Include the source channel for proper tracking.
    """
    # Implementation: Insert into tickets table
    # Returns: ticket_id
```

#### 4.3.3 get_customer_history

```python
@function_tool
async def get_customer_history(customer_id: str) -> str:
    """Get customer's complete interaction history across ALL channels.

    Use this to understand context from previous conversations,
    even if they happened on a different channel.
    """
    # Implementation: Query conversations and messages tables
    # Returns: Formatted history (last 20 interactions)
```

#### 4.3.4 escalate_to_human

```python
class EscalationInput(BaseModel):
    ticket_id: str
    reason: str
    urgency: str = "normal"  # 'normal', 'high', 'urgent'

@function_tool
async def escalate_to_human(input: EscalationInput) -> str:
    """Escalate conversation to human support.

    Use this when:
    - Customer asks about pricing or refunds
    - Customer sentiment is negative
    - You cannot find relevant information
    - Customer explicitly requests human help
    """
    # Implementation: Update ticket status, publish to Kafka escalations topic
    # Returns: Escalation confirmation with expected response time
```

#### 4.3.5 send_response

```python
class ResponseInput(BaseModel):
    ticket_id: str
    message: str
    channel: Channel

@function_tool
async def send_response(input: ResponseInput) -> str:
    """Send response to customer via their preferred channel.

    The response will be automatically formatted for the channel.
    Email: Formal with greeting/signature
    WhatsApp: Concise and conversational
    Web: Semi-formal
    """
    # Implementation: Format for channel, send via appropriate handler
    # Returns: Delivery status
```

---

## 5. API Endpoints

### 5.1 Gmail Webhook

```python
@app.post("/webhooks/gmail")
async def gmail_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle Gmail push notifications via Pub/Sub."""
    # 1. Verify Pub/Sub message
    # 2. Fetch email via Gmail API
    # 3. Publish to Kafka tickets.incoming
    # 4. Return 200 OK
```

### 5.2 WhatsApp Webhook

```python
@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle incoming WhatsApp messages via Twilio webhook."""
    # 1. Validate Twilio signature
    # 2. Parse webhook data
    # 3. Publish to Kafka tickets.incoming
    # 4. Return TwiML response
```

### 5.3 Web Support Form

```python
@app.post("/support/submit")
async def submit_support_form(submission: SupportFormSubmission):
    """Handle support form submission."""
    # 1. Validate submission
    # 2. Create ticket
    # 3. Publish to Kafka tickets.incoming
    # 4. Return ticket_id
```

### 5.4 Ticket Status

```python
@app.get("/support/ticket/{ticket_id}")
async def get_ticket_status(ticket_id: str):
    """Get status and conversation history for a ticket."""
    # Returns: ticket status, messages, timestamps
```

### 5.5 Health Check

```python
@app.get("/health")
async def health_check():
    """System health check."""
    # Returns: status, timestamp, channel availability
```

---

## 6. Kafka Topics

### 6.1 Topic Definitions

```python
TOPICS = {
    'tickets_incoming': 'fte.tickets.incoming',
    'email_inbound': 'fte.channels.email.inbound',
    'whatsapp_inbound': 'fte.channels.whatsapp.inbound',
    'webform_inbound': 'fte.channels.webform.inbound',
    'email_outbound': 'fte.channels.email.outbound',
    'whatsapp_outbound': 'fte.channels.whatsapp.outbound',
    'escalations': 'fte.escalations',
    'metrics': 'fte.metrics',
    'dlq': 'fte.dlq'  # Dead letter queue
}
```

### 6.2 Message Format

```json
{
  "event_id": "uuid",
  "event_type": "ticket_created",
  "timestamp": "2026-02-25T12:00:00Z",
  "channel": "email",
  "customer_id": "uuid",
  "ticket_id": "uuid",
  "payload": {
    "content": "Customer message",
    "metadata": {}
  }
}
```

---

## 7. Channel-Specific Requirements

### 7.1 Email (Gmail)

**Authentication:** OAuth 2.0
**Webhook:** Google Pub/Sub push notifications
**Send Method:** Gmail API
**Response Format:**
```
Dear Customer,

Thank you for reaching out to TaskNest Support.

[RESPONSE]

Best regards,
TaskNest Support Team
---
Ticket Reference: {ticket_id}
```
**Max Length:** 2000 characters

### 7.2 WhatsApp (Twilio)

**Authentication:** Twilio API credentials
**Webhook:** Twilio webhook with signature validation
**Send Method:** Twilio Messages API
**Response Format:**
```
[CONCISE RESPONSE]

📱 Reply for help or type 'human' for live support.
```
**Max Length:** 1600 characters (prefer <300)

### 7.3 Web Support Form

**Frontend:** Next.js 14 React component
**API:** POST /support/submit
**Response Format:**
```
[RESPONSE]

---
Need more help? Reply or visit support portal.
```
**Max Length:** 1000 characters

---

## 8. Non-Functional Requirements

### 8.1 Performance

- **Response Time:** P95 < 3 seconds
- **Throughput:** 100+ concurrent conversations
- **Latency:** Agent execution < 2 seconds

### 8.2 Availability

- **Uptime:** 99.9% (8.76 hours downtime/year)
- **Recovery Time:** < 5 minutes
- **Data Durability:** 99.999999999% (11 nines)

### 8.3 Scalability

- **Horizontal Scaling:** Auto-scale based on CPU/memory
- **Database:** Connection pooling, read replicas
- **Kafka:** Multiple consumer groups for parallel processing

### 8.4 Security

- **Data Encryption:** TLS 1.3 in transit, AES-256 at rest
- **Authentication:** OAuth 2.0, API keys
- **Authorization:** Role-based access control
- **PII Protection:** No PII in logs, sanitized before embedding

### 8.5 Monitoring

- **Metrics:** Prometheus + Grafana
- **Logging:** Structured JSON logs
- **Tracing:** Distributed tracing with correlation IDs
- **Alerts:** PagerDuty integration for critical issues

---

## 9. Testing Strategy

### 9.1 Unit Tests

- Tool functions (5 tools)
- Database operations
- Channel handlers
- Response formatters

### 9.2 Integration Tests

- End-to-end flow per channel
- Cross-channel customer identification
- Escalation workflows
- Kafka message processing

### 9.3 Load Tests

- 100+ concurrent users
- 500+ tickets per day
- Sustained load for 1 hour

### 9.4 Chaos Tests

- Random pod kills
- Database connection failures
- Kafka broker failures
- Network partitions

---

## 10. Deployment

### 10.1 Kubernetes Resources

**Deployments:**
- `fte-api` (3 replicas)
- `fte-message-processor` (3 replicas)

**Services:**
- `customer-success-fte` (LoadBalancer)

**ConfigMaps:**
- `fte-config` (environment variables)

**Secrets:**
- `fte-secrets` (API keys, credentials)

**HPA:**
- API: 3-20 replicas (70% CPU)
- Workers: 3-30 replicas (70% CPU)

### 10.2 CI/CD Pipeline

1. **Build:** Docker images
2. **Test:** Unit + integration tests
3. **Deploy:** Kubernetes rolling update
4. **Verify:** Health checks + smoke tests
5. **Monitor:** Metrics + alerts

---

## 11. Success Metrics

### 11.1 Primary KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Resolution Rate | >70% | Tickets resolved without escalation |
| Response Time | <3s | P95 latency |
| Escalation Rate | <25% | Tickets escalated to humans |
| Uptime | 99.9% | System availability |
| Customer Satisfaction | >4.0/5.0 | Post-interaction survey |

### 11.2 Secondary KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cross-Channel ID | >95% | Customer identification accuracy |
| Knowledge Hit Rate | >80% | Successful knowledge base searches |
| Sentiment Accuracy | >90% | Correct sentiment detection |
| First Contact Resolution | >60% | Resolved in first interaction |

---

## 12. Risks & Mitigations

### 12.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| OpenAI API downtime | High | Low | Implement retry logic, fallback responses |
| Database connection pool exhaustion | High | Medium | Connection pooling, monitoring, auto-scaling |
| Kafka message loss | High | Low | Persistent topics, replication factor 3 |
| Gmail API rate limits | Medium | Medium | Request batching, exponential backoff |

### 12.2 Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Poor customer experience | High | Medium | Extensive testing, gradual rollout |
| High escalation rate | Medium | Medium | Continuous knowledge base improvement |
| Security breach | High | Low | Security audits, penetration testing |

---

## 13. Timeline

### Phase 1: Incubation (Complete)
- ✅ Context files created
- ✅ Discovery log documented
- ✅ Specification crystallized

### Phase 2: Specialization (32 hours)
- Database schema implementation (4 hours)
- OpenAI Agent implementation (6 hours)
- Channel integrations (8 hours)
- Kafka setup (4 hours)
- FastAPI service (6 hours)
- Kubernetes deployment (4 hours)

### Phase 3: Testing (24 hours)
- E2E testing (8 hours)
- Load testing (8 hours)
- 24-hour continuous operation test (8 hours)

---

## 14. Appendices

### 14.1 Glossary

- **Digital FTE:** Full-Time Equivalent - AI employee working 24/7
- **Escalation:** Transferring conversation to human agent
- **Channel:** Communication medium (email, WhatsApp, web form)
- **Sentiment:** Emotional tone of customer message (0-1 scale)
- **Resolution Rate:** Percentage of tickets resolved without human intervention

### 14.2 References

- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/agents)
- [Neon PostgreSQL Documentation](https://neon.tech/docs)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)

---

**Specification Version:** 1.0
**Last Updated:** February 25, 2026
**Status:** Approved for Implementation
**Approved By:** Jennifer Park, Head of Customer Success

**Next Phase:** Specialization (Phase 2) - Production Implementation
