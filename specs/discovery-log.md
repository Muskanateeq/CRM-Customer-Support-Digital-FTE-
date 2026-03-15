# Discovery Log - TaskNest Customer Success AI Agent

## Purpose
This document captures insights, patterns, and requirements discovered during the incubation phase by analyzing 55+ sample customer tickets across email, WhatsApp, and web form channels.

**Date:** February 25, 2026
**Phase:** Incubation (Phase 1)
**Analyst:** AI Agent Development Team

---

## 📊 Ticket Analysis Summary

### Volume Distribution
- **Total Tickets Analyzed:** 55
- **Email:** 20 tickets (36%)
- **WhatsApp:** 20 tickets (36%)
- **Web Form:** 15 tickets (27%)

### Category Breakdown
- **General Questions:** 15 (27%) - Basic feature usage, plan info
- **Technical Issues:** 15 (27%) - Bugs, syncing, troubleshooting
- **Billing:** 10 (18%) - Pricing, refunds, invoices
- **Account Management:** 7 (13%) - Password, settings, profile
- **Integrations:** 5 (9%) - Slack, GitHub, calendar sync
- **Security:** 3 (5%) - GDPR, HIPAA, data concerns
- **Legal:** 2 (4%) - Threats, lawsuits
- **Explicit Escalation:** 2 (4%) - "human", "agent" requests

### Resolution Capability
- **AI Can Handle:** 42 tickets (76%)
- **Must Escalate:** 13 tickets (24%)

### Priority Distribution
- **Low:** 20 (36%)
- **Medium:** 22 (40%)
- **High:** 10 (18%)
- **Urgent:** 3 (5%)

---

## 🔍 Key Patterns Discovered

### Pattern 1: Channel-Specific Communication Styles

**Discovery:**
Customers communicate differently based on channel:

**Email:**
- Longer, more detailed messages
- More formal language
- Often includes context and history
- Expects comprehensive responses
- Average length: 150-300 words

**WhatsApp:**
- Very short messages (often 1-2 sentences)
- Casual, conversational tone
- Expects quick, concise answers
- Uses keywords like "human" or "agent" for escalation
- Average length: 10-30 words

**Web Form:**
- Structured with subject line
- Medium length (50-150 words)
- More organized than email
- Often includes category selection
- Expects semi-formal response

**Implication:** AI agent must adapt response length and tone based on channel.

---

### Pattern 2: Escalation Triggers are Clear

**Discovery:**
13 out of 55 tickets (24%) require human escalation, falling into predictable categories:

**Mandatory Escalation (9 tickets):**
1. **Billing/Refunds:** 5 tickets
   - "I want a refund"
   - "Charged twice"
   - "Pricing quote"

2. **Legal Threats:** 2 tickets
   - "Our lawyer will contact you"
   - "We will sue for damages"

3. **Security Incidents:** 1 ticket
   - "Account was hacked"

4. **Enterprise Features:** 1 ticket
   - "SSO setup for Enterprise"

**Conditional Escalation (4 tickets):**
1. **Explicit Requests:** 2 tickets
   - WhatsApp: "human" or "agent"

2. **Negative Sentiment:** 2 tickets
   - "This is unacceptable"
   - "Worst service ever"

**Implication:** Clear escalation rules can be codified. AI should never attempt to handle billing, legal, or security issues.

---

### Pattern 3: 76% of Queries are Routine and Documented

**Discovery:**
42 out of 55 tickets can be resolved using existing product documentation:

**Most Common Resolvable Issues:**
1. **Password Reset:** 3 tickets - Standard process documented
2. **Feature Questions:** 12 tickets - All in product docs
3. **Integration Setup:** 4 tickets - Step-by-step guides available
4. **Troubleshooting:** 8 tickets - Documented solutions exist
5. **Account Settings:** 5 tickets - Settings documentation complete
6. **Plan Comparisons:** 4 tickets - Pricing page has details
7. **Mobile App Questions:** 3 tickets - Mobile docs available
8. **Data Export/Privacy:** 3 tickets - Privacy section covers this

**Implication:** A well-implemented knowledge base search tool can resolve majority of tickets.

---

### Pattern 4: Cross-Channel Customer Tracking is Critical

**Discovery:**
Several scenarios indicate customers may contact via multiple channels:

**Scenario Examples:**
- Customer emails about issue, then follows up via WhatsApp
- Customer submits web form, doesn't get response, calls via WhatsApp
- Customer has history across multiple channels

**Current Gap:**
Sample tickets don't show explicit cross-channel scenarios, but real-world usage will require:
- Customer identification by email OR phone
- Conversation history spanning all channels
- Context preservation when switching channels

**Implication:** Database schema must support:
- `customer_identifiers` table linking email, phone, and other IDs
- `conversations` table tracking `initial_channel` but allowing channel switches
- `messages` table with channel field for each message

---

### Pattern 5: Sentiment Detection is Essential

**Discovery:**
Negative sentiment appears in 4 tickets (7%), requiring special handling:

**Negative Sentiment Indicators:**
- "This is ridiculous"
- "Worst service ever"
- "Unacceptable"
- "Terrible"
- Profanity (implied in some tickets)

**Positive/Neutral Sentiment:**
- Most tickets are neutral, factual questions
- Some show mild frustration but not anger

**Implication:**
- AI must detect sentiment in real-time
- Negative sentiment (score < 0.3) should trigger empathetic response
- Persistent negative sentiment after 2 exchanges → escalate

---

### Pattern 6: Response Time Expectations Vary by Channel

**Discovery:**
Implicit expectations based on channel:

**WhatsApp:**
- Customers expect near-instant response (< 1 minute)
- Real-time chat mentality
- Short back-and-forth acceptable

**Web Form:**
- Customers expect response within hours (2-4 hours)
- One comprehensive response preferred
- Ticket tracking expected

**Email:**
- Customers expect response within 4-24 hours
- Detailed, thorough response expected
- Thread continuity important

**Implication:** AI agent must respond within 3 seconds regardless of channel, but communication style should match channel expectations.

---

### Pattern 7: Common Troubleshooting Follows Predictable Paths

**Discovery:**
Technical issues follow standard troubleshooting patterns:

**Syncing Issues (3 tickets):**
1. Refresh browser
2. Check internet connection
3. Log out/log in
4. Clear cache
5. Try different browser
6. If still failing → escalate

**File Upload Issues (2 tickets):**
1. Check file size (100MB limit)
2. Check file format
3. Check internet connection
4. Try smaller file
5. Check storage quota
6. If still failing → escalate

**Integration Issues (3 tickets):**
1. Disconnect integration
2. Reconnect integration
3. Check authorization
4. Verify permissions
5. Check integration status page
6. If still failing → escalate

**Implication:** Troubleshooting can be systematized into decision trees for AI agent tools.

---

### Pattern 8: Feature Discovery vs. Feature Requests

**Discovery:**
Some "feature requests" are actually existing features customers don't know about:

**Examples:**
- "Can I create recurring tasks?" → YES, feature exists
- "Can I assign to multiple people?" → YES, feature exists
- "Does TaskNest work offline?" → YES, mobile apps do
- "Can I integrate with Slack?" → YES, integration available

**True Feature Requests:**
- "Can you add [new feature]?" → Feature doesn't exist

**Implication:**
- AI must search knowledge base thoroughly before assuming feature doesn't exist
- If feature exists, guide customer to it
- If feature doesn't exist, acknowledge request and escalate to product team

---

### Pattern 9: Billing Questions Have Clear Boundaries

**Discovery:**
Billing questions fall into two categories:

**AI Can Handle (5 tickets):**
- Plan comparisons
- Billing cycle explanation
- Invoice download location
- Downgrade process
- Trial expiration policy

**Must Escalate (5 tickets):**
- Refund requests
- Pricing negotiations
- Custom quotes
- Billing disputes
- Discount requests

**Implication:** AI must recognize the boundary and never attempt financial transactions.

---

### Pattern 10: Security and Compliance Questions are High-Stakes

**Discovery:**
Security questions require careful handling:

**Can Provide Information (2 tickets):**
- GDPR compliance → documented
- Data encryption → documented
- 2FA setup → documented

**Must Escalate (3 tickets):**
- Security incidents (hacking)
- HIPAA compliance with BAA
- Legal compliance documents

**Implication:** AI can provide general security information but must escalate incidents and legal compliance matters.

---

## 🎯 Requirements Crystallized from Patterns

### Functional Requirements

**FR1: Multi-Channel Support**
- Support email, WhatsApp, and web form
- Adapt response style per channel
- Maintain conversation context across channels

**FR2: Knowledge Base Search**
- Vector similarity search using embeddings
- Search product documentation
- Return top 5 relevant results
- Confidence scoring

**FR3: Customer Identification**
- Identify by email OR phone
- Link multiple identifiers to single customer
- Retrieve cross-channel history

**FR4: Ticket Management**
- Create ticket for every conversation
- Track status (open, processing, resolved, escalated)
- Store channel source
- Assign priority

**FR5: Escalation Logic**
- Detect escalation triggers (legal, billing, security)
- Detect negative sentiment
- Handle explicit escalation requests
- Provide context to human agents

**FR6: Sentiment Analysis**
- Real-time sentiment scoring (0-1 scale)
- Trigger empathetic responses for negative sentiment
- Escalate if sentiment remains negative after 2 exchanges

**FR7: Response Formatting**
- Email: Formal, detailed (up to 2000 chars)
- WhatsApp: Concise, casual (prefer <300 chars, max 1600)
- Web Form: Semi-formal, organized (up to 1000 chars)

**FR8: Conversation History**
- Store all messages (inbound/outbound)
- Track conversation flow
- Preserve context for follow-ups

### Non-Functional Requirements

**NFR1: Response Time**
- P95 latency < 3 seconds
- Real-time processing

**NFR2: Availability**
- 99.9% uptime
- 24/7 operation

**NFR3: Accuracy**
- >70% resolution rate without escalation
- <25% escalation rate
- >95% customer satisfaction

**NFR4: Scalability**
- Handle 100+ concurrent conversations
- Process 500+ tickets per day
- Auto-scale based on load

**NFR5: Data Security**
- No PII in logs
- Encrypted data storage
- Secure API communications

---

## 🛠️ Technical Architecture Insights

### Required Tools (Minimum 5)

Based on pattern analysis, AI agent needs these tools:

1. **search_knowledge_base**
   - Input: query string, max_results
   - Output: Relevant documentation snippets
   - Use: 76% of tickets need this

2. **create_ticket**
   - Input: customer_id, issue, priority, category, channel
   - Output: ticket_id
   - Use: Every conversation needs this

3. **get_customer_history**
   - Input: customer_id
   - Output: Previous conversations across all channels
   - Use: Context for returning customers

4. **escalate_to_human**
   - Input: ticket_id, reason, urgency
   - Output: Escalation confirmation
   - Use: 24% of tickets need this

5. **send_response**
   - Input: ticket_id, message, channel
   - Output: Delivery status
   - Use: Every response needs channel-appropriate formatting

### Database Schema Requirements

**Tables Needed:**
1. `customers` - Master customer record
2. `customer_identifiers` - Email, phone, other IDs
3. `conversations` - Conversation tracking
4. `messages` - All messages with channel info
5. `tickets` - Support tickets
6. `knowledge_base` - Product docs with embeddings

### Event Streaming Requirements

**Kafka Topics:**
- `tickets.incoming` - All new tickets
- `email.inbound` - Email messages
- `whatsapp.inbound` - WhatsApp messages
- `webform.inbound` - Web form submissions
- `escalations` - Escalated tickets
- `metrics` - Performance metrics

---

## 📈 Success Metrics Defined

Based on analysis, these metrics will indicate success:

**Primary Metrics:**
1. **Resolution Rate:** >70% (42/55 = 76% in sample)
2. **Escalation Rate:** <25% (13/55 = 24% in sample)
3. **Response Time:** <3 seconds
4. **Customer Satisfaction:** >4.0/5.0

**Secondary Metrics:**
1. **Cross-Channel Identification:** >95% accuracy
2. **Knowledge Base Hit Rate:** >80%
3. **Sentiment Detection Accuracy:** >90%
4. **First Contact Resolution:** >60%

---

## 🚧 Identified Challenges

### Challenge 1: WhatsApp Message Length
**Issue:** WhatsApp has 1600 char limit, but some answers need more detail
**Solution:** Break long responses into multiple messages OR provide summary + link to docs

### Challenge 2: Ambiguous Queries
**Issue:** Some customer messages are vague ("It's not working")
**Solution:** AI must ask clarifying questions before searching knowledge base

### Challenge 3: Multiple Issues in One Message
**Issue:** Customer mentions 3 different problems in one email
**Solution:** Address each issue separately, escalate if any requires escalation

### Challenge 4: False Positive Escalations
**Issue:** Keywords like "lawyer" might appear in non-threatening context
**Solution:** Context-aware escalation detection, not just keyword matching

### Challenge 5: Knowledge Base Gaps
**Issue:** Some questions might not be in documentation
**Solution:** After 2 failed searches, escalate with note to update docs

---

## 🎓 Lessons Learned

1. **Documentation Quality Matters:** 76% resolution rate depends on comprehensive, searchable docs
2. **Channel Adaptation is Critical:** One-size-fits-all responses won't work
3. **Escalation Rules Must Be Clear:** Ambiguity leads to poor customer experience
4. **Sentiment is a Strong Signal:** Negative sentiment requires immediate attention
5. **Cross-Channel Tracking is Complex:** Requires robust customer identification system

---

## ✅ Next Steps (Moving to Specification)

Based on discoveries, next phase will:

1. **Create formal specification** (customer-success-fte-spec.md)
2. **Build MCP server** with 5 tools
3. **Implement prototype** with OpenAI Agents SDK
4. **Test against sample tickets** to validate 76% resolution rate
5. **Refine based on results**

---

**Discovery Phase Complete:** February 25, 2026
**Confidence Level:** High - Patterns are clear and actionable
**Ready for Specialization Phase:** Yes

---

**Prepared by:** AI Agent Development Team
**Reviewed by:** Jennifer Park, Head of Customer Success
**Approved for Next Phase:** ✅
