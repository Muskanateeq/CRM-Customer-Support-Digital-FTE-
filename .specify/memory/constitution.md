# CRM Digital FTE Factory Constitution
**Hackathon 5 - Build Your First 24/7 AI Employee**

**Version:** 1.0 | **Ratified:** 2026-02-25 | **Status:** ACTIVE

---

## Core Principles

### I. Multi-Channel First
Every feature must support all three channels (Email, WhatsApp, Web Form) from day one. Channel-specific logic isolated in handlers. Cross-channel customer identification is mandatory.

### II. Event-Driven Architecture (NON-NEGOTIABLE)
All inter-service communication via Kafka. No direct service-to-service calls. Message processors are idempotent. Dead letter queues for failed messages.

### III. OpenAI Agents SDK (NON-NEGOTIABLE)
Agent implementation MUST use OpenAI Agents SDK, not custom implementations. Tools defined with strict typing (Pydantic). Agent instructions comprehensive and channel-aware.

### IV. Neon PostgreSQL as CRM
No external CRM systems (Salesforce, HubSpot). PostgreSQL IS the CRM. Schema normalized (customers, conversations, messages, tickets). pgvector for knowledge base embeddings.

### V. Production-Ready from Start
Code must be production-grade: async/await everywhere, proper error handling, logging, type hints, security best practices. No "we'll fix it later" approach.

### VI. Spec-Driven Development
All requirements documented before implementation. Discovery log maintained during incubation. Specifications crystallized before specialization phase.

---

## Technical Stack (LOCKED)

### Backend
- **Language:** Python 3.11+
- **API Framework:** FastAPI (async)
- **Agent SDK:** OpenAI Agents SDK (gpt-4o)
- **Database:** Neon PostgreSQL (serverless, pgvector)
- **Event Streaming:** Apache Kafka (aiokafka)
- **DB Driver:** asyncpg

### Frontend
- **Framework:** Next.js 14.2.x (App Router)
- **Language:** TypeScript
- **Styling:** TailwindCSS
- **UI Library:** React 18

### Integrations
- **Email:** Gmail API (OAuth 2.0 + Google Pub/Sub)
- **WhatsApp:** Twilio API (webhooks)
- **AI:** OpenAI API (GPT-4o)

### Infrastructure
- **Containers:** Docker
- **Orchestration:** Kubernetes
- **Local Testing:** Minikube

---

## Architecture Pattern

**Event-Driven Microservices:**
```
Channels → FastAPI Gateway → Kafka Topics → Workers → Agent → Database → Response
```

**Key Components:**
1. **FastAPI Gateway** - Webhook endpoints, validation, Kafka publishing
2. **Kafka Event Bus** - Decoupled message routing
3. **Message Processor Workers** - Consumer groups, agent execution
4. **OpenAI Agent** - Tool-based reasoning, channel-aware responses
5. **Neon PostgreSQL** - CRM data, conversation history, knowledge base

---

## Database Schema (CRM Core)

### customers
- id (UUID, PK)
- email (unique, nullable)
- phone (nullable)
- name, created_at, updated_at

### customer_identifiers
- id (UUID, PK)
- customer_id (FK)
- identifier_type (email, whatsapp, phone)
- identifier_value (unique)
- verified (boolean)

### conversations
- id (UUID, PK)
- customer_id (FK)
- initial_channel (enum)
- status (active, resolved, escalated)
- sentiment_score (float)
- started_at, ended_at

### messages
- id (UUID, PK)
- conversation_id (FK)
- role (customer, agent, system)
- content (text)
- channel (enum)
- direction (inbound, outbound)
- channel_message_id
- created_at, metadata (jsonb)

### tickets
- id (UUID, PK)
- customer_id (FK)
- conversation_id (FK)
- category, priority, status
- source_channel
- created_at, resolved_at

### knowledge_base
- id (UUID, PK)
- title, content
- category
- embedding (vector(1536))
- created_at, updated_at

---

## OpenAI Agent Specification

**Agent Identity:**
- Name: Customer Success FTE
- Model: gpt-4o
- Temperature: 0.7

**Tools (5 Required):**
1. `search_knowledge_base` - Vector similarity search
2. `create_ticket` - Support ticket creation
3. `get_customer_history` - Cross-channel history
4. `escalate_to_human` - Human handoff
5. `send_response` - Channel-aware sending

**System Prompt Rules:**
- ALWAYS create ticket at conversation start
- Check customer history ACROSS ALL CHANNELS
- Search knowledge base before answering
- Adapt tone to channel (formal email, casual WhatsApp, semi-formal web)
- Monitor sentiment - escalate if negative
- NEVER discuss pricing - escalate immediately
- NEVER promise undocumented features
- NEVER process refunds - escalate to billing

**Escalation Triggers:**
- Legal threats ("lawyer", "sue")
- Profanity or aggression
- Cannot find answer after 2 searches
- Customer explicitly requests human
- WhatsApp: "human" or "agent" keywords

---

## Channel Integration Requirements

### Gmail (REQUIRED)
- OAuth 2.0 authentication
- Google Pub/Sub push notifications
- Webhook: `/webhooks/gmail`
- Send via Gmail API
- Thread continuity maintained

### WhatsApp (REQUIRED)
- Twilio API integration
- Webhook signature validation
- Webhook: `/webhooks/whatsapp`
- Message length limits (1600 chars)
- Status callbacks handled

### Web Support Form (REQUIRED - MUST BUILD)
- Next.js 14 React component
- Fields: name, email, subject, category, priority, message
- Client-side validation
- API: `/support/submit`
- Status check: `/support/ticket/{id}`
- Email notification on response

---

## Channel-Aware Response Formatting

**Email:**
```
Dear Customer,

Thank you for reaching out to TechCorp Support.

[RESPONSE]

Best regards,
TechCorp AI Support Team
---
Ticket: {ticket_id}
```

**WhatsApp:**
```
[CONCISE RESPONSE - max 300 chars preferred]

📱 Reply for help or type 'human' for live support.
```

**Web Form:**
```
[RESPONSE]

---
Need more help? Reply or visit support portal.
```

---

## Development Phases

### Phase 1: Incubation (Hours 1-16)
**Objective:** Prototype with Claude Code

**Deliverables:**
- [ ] context/company-profile.md
- [ ] context/product-docs.md
- [ ] context/sample-tickets.json (50+ tickets)
- [ ] context/escalation-rules.md
- [ ] context/brand-voice.md
- [ ] specs/discovery-log.md
- [ ] specs/customer-success-fte-spec.md
- [ ] Working MCP server (5+ tools)
- [ ] Agent skills manifest
- [ ] Test dataset (20+ edge cases per channel)

### Phase 2: Specialization (Hours 17-48)
**Objective:** Production system

**Deliverables:**
- [ ] Neon PostgreSQL schema deployed
- [ ] OpenAI Agents SDK implementation
- [ ] FastAPI service (all endpoints)
- [ ] Gmail integration (OAuth + webhooks)
- [ ] WhatsApp integration (Twilio webhooks)
- [ ] Web Support Form (Next.js 14)
- [ ] Kafka event streaming (all topics)
- [ ] Message processor workers
- [ ] Kubernetes manifests (complete)
- [ ] Docker images built
- [ ] E2E test suite passing

### Phase 3: Integration & Testing (Hours 49-72)
**Objective:** 24-hour readiness

**Deliverables:**
- [ ] Multi-channel E2E tests passing
- [ ] Load test: 100+ req/min sustained
- [ ] Chaos test: Survives pod kills
- [ ] Monitoring configured
- [ ] Documentation complete
- [ ] Runbook for incidents

---

## Project Structure

```
hackathon5/
├── .specify/
│   └── memory/
│       └── constitution.md          # THIS FILE
├── context/                         # Phase 1 context
│   ├── company-profile.md
│   ├── product-docs.md
│   ├── sample-tickets.json
│   ├── escalation-rules.md
│   └── brand-voice.md
├── specs/                           # Phase 1 specs
│   ├── discovery-log.md
│   └── customer-success-fte-spec.md
├── src/                             # Phase 2 production code
│   ├── agent/
│   ├── channels/
│   ├── workers/
│   ├── api/
│   ├── database/
│   └── kafka_client.py
├── web-form/                        # Next.js 14 app
├── tests/                           # Test suites
├── k8s/                             # Kubernetes manifests
├── docker/                          # Dockerfiles
└── docs/                            # Documentation
```

---

## Coding Standards

### Python
- PEP 8 compliance (Black formatter)
- Type hints required for all functions
- async/await everywhere possible
- Proper error handling with logging
- Pydantic models for validation

### TypeScript/React
- ESLint + Prettier
- Functional components with hooks
- TailwindCSS utility classes
- Controlled components with validation

### Database
- SQL migrations in migrations/
- Parameterized queries (prevent SQL injection)
- Indexes on foreign keys and search columns
- snake_case naming

### API
- REST standards (GET, POST, PUT, DELETE)
- Proper status codes (200, 201, 400, 404, 500)
- Pydantic validation for all inputs
- CORS enabled for web form

---

## Security Requirements

1. **Secrets Management:**
   - NEVER commit credentials to git
   - Use .env files (add to .gitignore)
   - Kubernetes secrets for production

2. **API Security:**
   - Validate Twilio webhook signatures
   - Verify Gmail Pub/Sub messages
   - Rate limiting on public endpoints
   - Input sanitization (XSS, SQL injection prevention)

3. **Database:**
   - Connection pooling
   - Parameterized queries only
   - Least privilege access

4. **Agent Safety:**
   - No PII in logs
   - Sanitize customer data before embedding
   - Timeout on agent runs (30s max)

---

## Acceptance Criteria

### Functional Requirements
- [ ] Agent responds in <5 seconds
- [ ] Cross-channel customer identification works
- [ ] Knowledge base search returns relevant results
- [ ] Escalation triggers work correctly
- [ ] All 3 channels operational
- [ ] Responses formatted per channel
- [ ] Conversation history persists across channels

### Non-Functional Requirements
- [ ] 99.9% uptime during 24-hour test
- [ ] P95 latency < 3 seconds
- [ ] Handles 100+ concurrent requests
- [ ] Survives pod restarts (no data loss)
- [ ] Scales horizontally (HPA working)
- [ ] No message loss (Kafka guarantees)
- [ ] Escalation rate < 25%

---

## Scoring Rubric (100 Points)

**Technical Implementation (50 points)**
- Incubation Quality: 10
- Agent Implementation: 10
- Web Support Form: 10 (REQUIRED)
- Channel Integrations: 10
- Database & Kafka: 5
- Kubernetes Deployment: 5

**Operational Excellence (25 points)**
- 24/7 Readiness: 10
- Cross-Channel Continuity: 10
- Monitoring: 5

**Business Value (15 points)**
- Customer Experience: 10
- Documentation: 5

**Innovation (10 points)**
- Creative Solutions: 5
- Evolution Demonstration: 5

**Passing Score:** 70/100 | **Excellence:** 85/100

---

## Critical Success Factors (NON-NEGOTIABLE)

1. ✅ Web Support Form is MANDATORY
2. ✅ OpenAI Agents SDK must be used
3. ✅ Multi-channel support (all 3 channels)
4. ✅ Cross-channel continuity (customer history spans channels)
5. ✅ 24-hour test must pass
6. ✅ No external CRM (PostgreSQL IS the CRM)

---

## Final Challenge: 24-Hour Multi-Channel Test

**Test Requirements:**
- 100+ web form submissions
- 50+ Gmail messages processed
- 50+ WhatsApp messages processed
- 10+ cross-channel customers
- Random pod kills every 2 hours

**Success Metrics:**
- Uptime > 99.9%
- P95 latency < 3 seconds
- Escalation rate < 25%
- Cross-channel identification > 95%
- No message loss

---

## Governance

**This constitution supersedes all other practices.**

**Amendments require:**
- Documentation of reason
- Update to this file
- Version increment
- Approval (from you, the student)

**All implementation decisions must:**
- Verify compliance with this constitution
- Reference specific sections when making choices
- Document deviations with justification

**MCP Servers Available:**
- Neon PostgreSQL MCP (database operations)
- Context7 MCP (OpenAI Agents SDK + Kafka documentation)

---

**Version:** 1.0 | **Ratified:** 2026-02-25 | **Last Amended:** 2026-02-25

**This is the law of the land. All decisions flow from this document.**
