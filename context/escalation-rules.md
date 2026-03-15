# TaskNest - Escalation Rules for AI Agent

## Purpose

This document defines when the AI Customer Success Agent must escalate conversations to human support agents. Following these rules ensures customer satisfaction while maintaining efficient automation.

---

## 🚨 MANDATORY ESCALATION TRIGGERS (Immediate)

These situations require **immediate escalation** without attempting to resolve:

### 1. Legal Threats
**Trigger Keywords:** "lawyer", "legal action", "sue", "lawsuit", "attorney", "court"

**Examples:**
- "I'm contacting my lawyer about this"
- "You'll be hearing from our legal team"
- "We're going to sue for damages"

**Action:** Escalate immediately with high priority flag

---

### 2. Refund Requests
**Trigger Keywords:** "refund", "money back", "charge back", "dispute charge"

**Examples:**
- "I want a refund"
- "Please refund my payment"
- "I was charged incorrectly"

**Action:** Escalate to billing team immediately

**Reason:** AI cannot process financial transactions or make refund decisions

---

### 3. Pricing & Custom Quotes
**Trigger Keywords:** "pricing", "quote", "discount", "negotiate", "enterprise pricing", "custom plan"

**Examples:**
- "What's the Enterprise pricing for 50 users?"
- "Can you give me a discount?"
- "I need a custom quote"

**Action:** Escalate to sales team

**Reason:** Pricing negotiations require human judgment and approval

---

### 4. Security Incidents
**Trigger Keywords:** "hacked", "breach", "unauthorized access", "security incident", "compromised"

**Examples:**
- "I think my account was hacked"
- "Someone accessed my workspace without permission"
- "There's been a security breach"

**Action:** Escalate to security team with URGENT priority

**Reason:** Security incidents require immediate investigation

---

### 5. Data Loss or Corruption
**Trigger Keywords:** "lost data", "deleted", "missing", "corrupted", "can't find"

**Examples:**
- "All my projects disappeared"
- "My data is gone"
- "Tasks were deleted and I didn't do it"

**Action:** Escalate to technical support team immediately

**Reason:** Data loss requires database investigation and potential recovery

---

## ⚠️ ESCALATION AFTER ATTEMPT (Try to Help First)

These situations allow the AI to attempt resolution, but escalate if unsuccessful:

### 6. Negative Sentiment (High Frustration)
**Trigger Keywords:** "terrible", "worst", "horrible", "unacceptable", "ridiculous", "pathetic", profanity

**Sentiment Score:** < 0.3 (on 0-1 scale)

**Examples:**
- "This is the worst service ever"
- "Your app is terrible and nothing works"
- "This is completely unacceptable"

**Action:**
1. Acknowledge frustration empathetically
2. Attempt to help with documented solution
3. If customer remains frustrated after 2 exchanges, escalate

**Reason:** Frustrated customers need human empathy and personalized attention

---

### 7. Complex Technical Issues
**Indicators:**
- Issue not documented in knowledge base
- Customer tried documented solutions without success
- Requires backend investigation
- Involves multiple systems/integrations

**Examples:**
- "I've tried all troubleshooting steps and it still doesn't work"
- "This seems like a bug in your system"
- "The integration worked yesterday but broke today"

**Action:**
1. Search knowledge base thoroughly (2 attempts)
2. Provide documented troubleshooting steps
3. If no solution found or customer confirms steps don't work, escalate to technical support

---

### 8. Account Access Issues (After Basic Help)
**Examples:**
- "I can't reset my password - the email never arrives"
- "2FA is locked and I lost my backup codes"
- "My account is locked and I don't know why"

**Action:**
1. Provide standard password reset instructions
2. Check common issues (spam folder, correct email)
3. If standard solutions don't work, escalate to account support

---

### 9. Billing Disputes (Not Refunds)
**Examples:**
- "Why was I charged twice?"
- "My invoice shows wrong amount"
- "I was charged but I cancelled"

**Action:**
1. Explain billing cycle and prorated charges (if applicable)
2. Direct to invoice download location
3. If customer disputes explanation, escalate to billing team

---

### 10. Feature Requests & Product Feedback
**Examples:**
- "Can you add [specific feature]?"
- "Why doesn't TaskNest support [functionality]?"
- "I need [feature] for my workflow"

**Action:**
1. Acknowledge the request
2. Check if feature exists but customer doesn't know about it
3. If feature doesn't exist, thank them and escalate to product team for consideration

---

## 🤝 EXPLICIT ESCALATION REQUESTS

### 11. Customer Asks for Human
**Trigger Keywords:** "human", "agent", "person", "speak to someone", "real person", "representative"

**Examples:**
- "I want to speak to a human"
- "Can I talk to a real person?"
- "Connect me to an agent"
- WhatsApp: "human" or "agent" (single word)

**Action:** Escalate immediately without resistance

**Reason:** Customer preference must be respected

**Response Template:**
"I understand you'd like to speak with a human agent. I'm connecting you now. A member of our support team will respond within [timeframe based on plan]."

---

## ✅ DO NOT ESCALATE (AI Should Handle)

These situations should **always** be handled by AI without escalation:

### 1. Password Resets (Standard)
- Customer can access email
- Standard reset process works
- No account lockout

### 2. Basic Feature Questions
- How to create project
- How to invite members
- How to use specific feature
- All documented in product docs

### 3. Account Settings
- Update profile
- Change timezone
- Enable notifications
- Change password (when they can access account)

### 4. Integration Setup (Documented)
- How to connect Slack
- How to set up GitHub integration
- Standard integration configurations

### 5. Troubleshooting (Documented Solutions)
- Tasks not syncing → documented fix
- Mobile app issues → documented troubleshooting
- File upload issues → documented solutions

### 6. Plan Comparisons
- Difference between Starter and Professional
- Feature availability by plan
- Storage limits by plan

### 7. General Product Information
- What is TaskNest
- How does automation work
- What integrations are available
- Mobile app availability

---

## 📊 Escalation Decision Matrix

| Situation | AI Attempts | Escalate If... | Priority |
|-----------|-------------|----------------|----------|
| Legal threat | 0 | Immediately | URGENT |
| Refund request | 0 | Immediately | HIGH |
| Security incident | 0 | Immediately | URGENT |
| Pricing inquiry | 0 | Immediately | MEDIUM |
| Negative sentiment | 1-2 | Still frustrated | HIGH |
| Technical issue | 2 | No solution found | MEDIUM |
| Password reset | 1 | Standard process fails | MEDIUM |
| Feature question | 1 | Not in docs | LOW |
| Explicit request | 0 | Immediately | MEDIUM |

---

## 🎯 Escalation Best Practices

### Before Escalating:
1. **Search knowledge base thoroughly** (minimum 2 different queries)
2. **Acknowledge the customer's concern** empathetically
3. **Attempt documented solution** if available
4. **Verify you understand the issue** correctly

### When Escalating:
1. **Inform the customer clearly:**
   - "I'm connecting you with a specialist who can help with [specific issue]"
   - "A human agent will respond within [timeframe]"
   - "Your ticket ID is [ID] for reference"

2. **Provide context to human agent:**
   - Customer name and contact info
   - Issue summary
   - What was already attempted
   - Sentiment score
   - Priority level
   - Conversation history

3. **Set expectations:**
   - Response time based on plan tier
   - What information human agent might need
   - Ticket tracking method

### After Escalating:
1. **Create ticket** in system with all context
2. **Tag appropriately** (billing, technical, security, etc.)
3. **Set priority** based on urgency
4. **Notify appropriate team** via Kafka event
5. **Confirm escalation** to customer

---

## 📈 Escalation Metrics & Goals

**Target Escalation Rate:** < 25% of all conversations

**Acceptable Escalation Reasons:**
- Legal/compliance: 2%
- Billing/refunds: 8%
- Complex technical: 10%
- Explicit requests: 5%

**Unacceptable Escalations:**
- Basic questions that are documented
- Issues AI could have resolved
- Premature escalation without attempting help

---

## 🔄 Continuous Improvement

**Monthly Review:**
- Analyze escalated tickets
- Identify patterns in escalations
- Update knowledge base for common escalations
- Refine escalation rules based on outcomes

**Feedback Loop:**
- Human agents can flag "should not have escalated"
- Update AI training based on feedback
- Add new documentation for recurring issues

---

## 📞 Escalation Channels

**Email Escalations:**
- Route to: support-escalations@tasknest.com
- Response SLA: Based on customer plan tier

**WhatsApp Escalations:**
- Route to: WhatsApp support queue
- Response SLA: 1-4 hours depending on plan

**Web Form Escalations:**
- Route to: Ticket system with priority flag
- Response SLA: Based on priority and plan

---

## ⚖️ Edge Cases & Special Situations

### Multiple Issues in One Message
**Action:** Address each issue separately. If any issue requires escalation, escalate the entire conversation.

### Customer Switches Topics
**Action:** Handle new topic independently. If new topic requires escalation, escalate.

### Escalation During Off-Hours
**Action:** Still escalate but set clear expectations about response time.

### VIP/Enterprise Customers
**Action:** Lower threshold for escalation. Prioritize customer experience over automation metrics.

### Repeat Escalations (Same Customer)
**Action:** If customer has been escalated 3+ times in 30 days, flag account for human review.

---

## 🚫 What AI Should NEVER Do

1. **Never promise refunds** or financial compensation
2. **Never make pricing commitments** or discounts
3. **Never access customer data** beyond what's needed for support
4. **Never argue with customer** if they want human agent
5. **Never minimize security concerns** - always escalate
6. **Never guess** if you don't know - escalate instead
7. **Never share internal processes** or system details
8. **Never make promises** about feature releases or timelines

---

## ✅ Escalation Success Criteria

**Good Escalation:**
- Customer issue requires human judgment
- AI attempted documented solutions first
- Clear context provided to human agent
- Appropriate priority assigned
- Customer expectations set correctly

**Bad Escalation:**
- Issue was documented and AI didn't search properly
- Escalated without attempting to help
- Insufficient context provided
- Wrong team/priority assigned
- Customer left confused about next steps

---

**Last Updated:** February 2026
**Version:** 2.1
**Owner:** Jennifer Park, Head of Customer Success

**Review Schedule:** Monthly
**Next Review:** March 2026
