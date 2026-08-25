"""
Response Generator for Custora AI
Generates appropriate responses based on scenario classification
"""

from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI

from src.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ResponseGenerator:
    """
    Generates responses based on scenario type.
    Uses Groq LLM with scenario-specific prompts.
    """

    def __init__(self):
        """Initialize Groq client for response generation."""
        self.client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY
        )
        self.model = settings.GROQ_MODEL

    async def _create_completion(
        self,
        messages: List[Dict[str, str]],
    ) -> str:
        """Generate one complete answer and retry if the provider truncates it."""
        token_budget = settings.GROQ_MAX_COMPLETION_TOKENS

        for attempt in range(2):
            request_messages = list(messages)
            if attempt:
                request_messages[-1] = {
                    **request_messages[-1],
                    "content": (
                        request_messages[-1]["content"]
                        + "\n\nCRITICAL: Regenerate the entire response. It must be "
                        "complete, end naturally, and include every required closing "
                        "sentence. Never stop mid-sentence or mid-list."
                    ),
                }

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=request_messages,
                temperature=0.6,
                max_completion_tokens=token_budget,
                reasoning_effort=settings.GROQ_REASONING_EFFORT,
                extra_body={"include_reasoning": False},
            )

            choice = response.choices[0]
            content = (choice.message.content or "").strip()
            if content and choice.finish_reason != "length":
                return content

            logger.warning(
                "Groq response reached its completion limit; retrying with a "
                "larger budget"
            )
            token_budget = min(token_budget * 2, 8192)

        raise RuntimeError("Groq returned an incomplete response twice")

    async def generate_response(
        self,
        scenario: str,
        user_query: str,
        conversation_id: str,
        channel: str = "webform",
        kb_results: Optional[List[Dict[str, Any]]] = None,
        ticket_id: Optional[str] = None,
        classification: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate response based on scenario.

        Args:
            scenario: SCENARIO_1_ECOMMERCE, SCENARIO_2_OUT_OF_SCOPE, or SCENARIO_3_ESCALATION
            user_query: Customer's original query
            conversation_id: Conversation ID for logging
            channel: Communication channel (email, whatsapp, webform)
            kb_results: Knowledge base search results (for Scenario 1)
            ticket_id: Created ticket ID (for Scenario 1 and 3)
            classification: Full classification dict with category, priority, reasoning

        Returns:
            Generated response text
        """
        try:
            logger.info(f"Generating response for {scenario} [cid: {conversation_id[:8]}]")

            if scenario == "SCENARIO_1_ECOMMERCE":
                response = await self._generate_scenario_1_response(
                    user_query, kb_results, ticket_id, channel, classification
                )
            elif scenario == "SCENARIO_2_OUT_OF_SCOPE":
                response = await self._generate_scenario_2_response(
                    user_query, channel
                )
            elif scenario == "SCENARIO_3_ESCALATION":
                response = await self._generate_scenario_3_response(
                    user_query, ticket_id, channel, classification
                )
            else:
                # Fallback
                response = self._get_fallback_response(channel)

            logger.info(f"Response generated successfully [cid: {conversation_id[:8]}]")
            return response

        except Exception:
            # Let SmartAgent and the dual-mode router record the provider
            # failure instead of reporting a fallback template as success.
            logger.exception(
                f"Response generation failed [cid: {conversation_id[:8]}]"
            )
            raise

    async def _generate_scenario_1_response(
        self,
        user_query: str,
        kb_results: Optional[List[Dict[str, Any]]],
        ticket_id: Optional[str],
        channel: str,
        classification: Optional[Dict[str, Any]]
    ) -> str:
        """Generate helpful response for ecommerce queries."""

        # Format knowledge base results
        kb_context = ""
        if kb_results and len(kb_results) > 0:
            kb_context = "\n\nKNOWLEDGE BASE INFORMATION:\n"
            for i, result in enumerate(kb_results, 1):
                title = result.get('title', 'Untitled')
                content = result.get('content', '')[:300]  # Limit content length
                kb_context += f"{i}. {title}\n{content}...\n\n"
        else:
            kb_context = "\n\nNo specific knowledge base articles found. Use your general ecommerce knowledge.\n"

        category = classification.get('category', 'general') if classification else 'general'

        prompt = f"""
You are Custora AI, a helpful ecommerce customer support agent.

CUSTOMER QUERY: "{user_query}"

QUERY CATEGORY: {category}

{kb_context}

TICKET CREATED: #{ticket_id}

CHANNEL: {channel.upper()}

---

INSTRUCTIONS:

Generate a helpful, professional response that:

1. **Directly addresses the customer's question**
   - Use the knowledge base information if available
   - If KB is empty, use your general ecommerce knowledge
   - Be specific and actionable

2. **Provide clear next steps or solutions**
   - Tell them exactly what to do
   - Include links only when they exist in the knowledge base
   - Never invent product names, bundles, prices, policies, or URLs
   - If exact catalog data is unavailable, give safe general guidance and
     clearly say that specific availability must be checked in the store catalog

3. **Mention the tracking ticket at the END**
   - Format: "I've created tracking ticket #{ticket_id} for your reference."
   - This helps customer track their inquiry

4. **Maintain appropriate tone for {channel}**
   - Email: Formal, detailed
   - WhatsApp: Casual, concise
   - Webform: Semi-formal, clear

5. **Keep it concise but complete**
   - Maximum 200 words
   - Focus on solving their problem
   - Make headings, step counts, and numbered lists internally consistent
   - End every response naturally; never stop mid-sentence or mid-list

6. **Use clean Markdown formatting**
   - Use **bold** only for important headings or key actions
   - Use numbered or bullet lists where they improve readability
   - Do not use Markdown tables or raw HTML

---

RESPONSE:
"""

        return await self._create_completion(
            messages=[
                {"role": "system", "content": "You are Custora AI, a professional ecommerce customer support agent. Be helpful, clear, and concise."},
                {"role": "user", "content": prompt}
            ]
        )

    async def _generate_scenario_2_response(
        self,
        user_query: str,
        channel: str
    ) -> str:
        """Generate polite redirect for out-of-scope queries."""

        prompt = f"""
You are Custora AI, an ecommerce customer support agent.

CUSTOMER QUERY: "{user_query}"

This query is OUTSIDE your scope (not related to ecommerce/shopping).

CHANNEL: {channel.upper()}

---

INSTRUCTIONS:

Generate a polite response that:

1. **Apologizes for not being able to help with this specific query**
   - Be empathetic but firm
   - Don't try to answer their question

2. **Introduces yourself clearly**
   - "I'm Custora AI, your ecommerce customer support agent"

3. **Lists what you CAN help with**
   - Order tracking and status
   - Shipping and delivery
   - Returns and exchanges
   - Payment methods
   - Account management
   - Product information

4. **Suggests where they might find help**
   - Be helpful by redirecting them appropriately
   - Example: "You may want to search for [topic] on relevant educational/specialized platforms"

5. **Ends with an offer to help with ecommerce**
   - "Is there anything about your Custora AI shopping experience I can help with?"

6. **Maintain appropriate tone for {channel}**
   - Email: Formal
   - WhatsApp: Casual
   - Webform: Semi-formal

7. **Keep it brief**
   - Maximum 150 words
   - Don't over-explain

IMPORTANT:
- DO NOT create a ticket
- DO NOT provide a solution to their query
- DO NOT escalate to human

---

RESPONSE:
"""

        return await self._create_completion(
            messages=[
                {"role": "system", "content": "You are Custora AI. Politely redirect out-of-scope queries without solving them."},
                {"role": "user", "content": prompt}
            ]
        )

    async def _generate_scenario_3_response(
        self,
        user_query: str,
        ticket_id: Optional[str],
        channel: str,
        classification: Optional[Dict[str, Any]]
    ) -> str:
        """Generate empathetic escalation response."""

        priority = classification.get('priority', 'high') if classification else 'high'

        # Determine timeframe based on priority
        timeframe_map = {
            "urgent": "within 15 minutes",
            "high": "within 2 hours",
            "medium": "within 24 hours",
            "low": "within 48 hours"
        }
        timeframe = timeframe_map.get(priority, "soon")

        prompt = f"""
You are Custora AI, an empathetic ecommerce customer support agent.

CUSTOMER QUERY: "{user_query}"

SITUATION: This requires human intervention (escalation)

PRIORITY: {priority}
TICKET CREATED: #{ticket_id}
EXPECTED RESPONSE TIME: {timeframe}

CHANNEL: {channel.upper()}

---

INSTRUCTIONS:

Generate an empathetic escalation response that:

1. **Acknowledges their concern with empathy**
   - Show you understand this is important/urgent/frustrating
   - Use phrases like "I understand", "I can see why this is concerning"

2. **Clearly states you're escalating to the support team**
   - "I've escalated your case to our specialized support team"
   - Make them feel prioritized

3. **Provides the ticket ID**
   - Format: "Ticket #{ticket_id}"
   - This is their reference number

4. **Sets clear expectations**
   - "A human agent will contact you {timeframe}"
   - Be specific about timing

5. **Thanks them for patience**
   - Professional closing

6. **Maintain appropriate tone for {channel}**
   - Email: Formal, detailed
   - WhatsApp: Casual but professional
   - Webform: Semi-formal

7. **Keep it concise**
   - Maximum 100 words
   - Focus on reassurance

---

RESPONSE:
"""

        return await self._create_completion(
            messages=[
                {"role": "system", "content": "You are Custora AI. Provide empathetic escalation responses that reassure customers."},
                {"role": "user", "content": prompt}
            ]
        )

    def _get_fallback_response(self, channel: str) -> str:
        """Get fallback response when generation fails."""
        base_message = (
            "I apologize, but I'm experiencing technical difficulties at the moment. "
            "Your message has been recorded, and our support team will respond shortly."
        )

        if channel == "email":
            return (
                f"{base_message}\n\n"
                f"Best regards,\n"
                f"Custora AI Support Team\n"
                f"support@custoraai.com"
            )
        elif channel == "whatsapp":
            return f"{base_message}\n\n- Custora AI Support 🚀"
        else:  # webform
            return (
                f"{base_message}\n\n"
                f"If this is urgent, please email us at support@custoraai.com.\n"
                f"- Custora AI Support"
            )
