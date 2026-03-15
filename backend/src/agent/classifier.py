"""
Query Classification System for Custora AI
Classifies customer queries into 3 scenarios without using tool calling
"""

import json
import re
from typing import Dict, Any, Optional
from openai import AsyncOpenAI

from src.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class QueryClassifier:
    """
    Classifies customer queries into one of 3 scenarios:
    - SCENARIO_1_ECOMMERCE: Supported ecommerce queries (helpful response + ticket)
    - SCENARIO_2_OUT_OF_SCOPE: Out-of-scope queries (polite redirect, no ticket)
    - SCENARIO_3_ESCALATION: Escalation required (human escalation + ticket)
    """

    def __init__(self):
        """Initialize Groq client for classification."""
        self.client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY
        )
        self.model = "llama-3.3-70b-versatile"

    async def classify(self, user_query: str, conversation_id: str) -> Dict[str, Any]:
        """
        Classify user query into one of 3 scenarios.

        Args:
            user_query: Customer's message
            conversation_id: Conversation ID for logging

        Returns:
            Dict with scenario, category, priority, reasoning
        """
        try:
            logger.info(f"Classifying query [cid: {conversation_id[:8]}]")

            classification_prompt = self._build_classification_prompt(user_query)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a query classification expert. Return ONLY valid JSON, no other text."},
                    {"role": "user", "content": classification_prompt}
                ],
                temperature=0,  # Deterministic classification
                max_tokens=300
            )

            response_text = response.choices[0].message.content.strip()

            # Extract JSON from response (handle cases where model adds extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)

            classification = json.loads(response_text)

            # Validate classification
            if not self._validate_classification(classification):
                logger.warning(f"Invalid classification, using fallback [cid: {conversation_id[:8]}]")
                classification = self._get_fallback_classification(user_query)

            logger.info(f"Classification: {classification['scenario']} - {classification['category']} [cid: {conversation_id[:8]}]")
            return classification

        except Exception as e:
            logger.error(f"Classification failed: {e} [cid: {conversation_id[:8]}]")
            # Fallback to safe classification
            return self._get_fallback_classification(user_query)

    def _build_classification_prompt(self, user_query: str) -> str:
        """Build classification prompt."""
        return f"""
Classify this customer query for Custora AI (ecommerce platform) into ONE of THREE scenarios.

USER QUERY: "{user_query}"

---

SCENARIO DEFINITIONS:

**SCENARIO_1_ECOMMERCE**: Query is about ecommerce topics we support
- Categories: order_status, shipping, returns, payment, account, product, general
- Examples: "Where is my order?", "How do I return an item?", "What payment methods do you accept?"

**SCENARIO_2_OUT_OF_SCOPE**: Query is NOT about ecommerce/shopping
- Examples: "What is Python?", "How to cook pasta?", "Tell me about sports", "Weather forecast"
- NOT our domain - we only handle ecommerce

**SCENARIO_3_ESCALATION**: Requires human intervention (sensitive/urgent)
- Triggers: refund requests, damaged items, legal threats, security issues, explicit human request, very angry customer
- Examples: "I want a refund!", "Item arrived damaged", "I want to speak to a human", "This is fraud!"

---

CLASSIFICATION RULES:

1. If query mentions: refund, damaged, defective, wrong item, legal, lawyer, sue, fraud, hack, human agent, speak to person
   → SCENARIO_3_ESCALATION

2. If query is about: orders, shipping, delivery, returns, exchanges, payment methods, account, login, products, prices
   → SCENARIO_1_ECOMMERCE

3. If query is about: programming, cooking, sports, weather, education, unrelated topics
   → SCENARIO_2_OUT_OF_SCOPE

---

Return ONLY this JSON (no other text):

{{
  "scenario": "SCENARIO_1_ECOMMERCE" | "SCENARIO_2_OUT_OF_SCOPE" | "SCENARIO_3_ESCALATION",
  "category": "order_status" | "shipping" | "returns" | "payment" | "account" | "product" | "general" | "out_of_scope" | "escalation",
  "priority": "low" | "medium" | "high" | "urgent",
  "reasoning": "brief explanation in 1 sentence"
}}

IMPORTANT: Return ONLY the JSON object, nothing else.
"""

    def _validate_classification(self, classification: Dict[str, Any]) -> bool:
        """Validate classification structure."""
        required_keys = ["scenario", "category", "priority", "reasoning"]
        if not all(key in classification for key in required_keys):
            return False

        valid_scenarios = ["SCENARIO_1_ECOMMERCE", "SCENARIO_2_OUT_OF_SCOPE", "SCENARIO_3_ESCALATION"]
        if classification["scenario"] not in valid_scenarios:
            return False

        valid_priorities = ["low", "medium", "high", "urgent"]
        if classification["priority"] not in valid_priorities:
            return False

        return True

    def _get_fallback_classification(self, user_query: str) -> Dict[str, Any]:
        """
        Fallback classification using keyword matching.
        Used when LLM classification fails.
        """
        query_lower = user_query.lower()

        # Check for escalation keywords
        escalation_keywords = [
            "refund", "damaged", "defective", "wrong item", "broken",
            "legal", "lawyer", "sue", "fraud", "hack", "unauthorized",
            "human", "agent", "person", "speak to", "talk to",
            "angry", "furious", "terrible", "worst"
        ]
        if any(keyword in query_lower for keyword in escalation_keywords):
            return {
                "scenario": "SCENARIO_3_ESCALATION",
                "category": "escalation",
                "priority": "high",
                "reasoning": "Escalation keywords detected (fallback classification)"
            }

        # Check for ecommerce keywords
        ecommerce_keywords = [
            "order", "shipping", "delivery", "track", "return", "exchange",
            "payment", "pay", "account", "login", "password", "product",
            "item", "purchase", "buy", "cart", "checkout"
        ]
        if any(keyword in query_lower for keyword in ecommerce_keywords):
            # Determine category
            if any(k in query_lower for k in ["order", "track", "status"]):
                category = "order_status"
            elif any(k in query_lower for k in ["ship", "delivery", "deliver"]):
                category = "shipping"
            elif any(k in query_lower for k in ["return", "exchange"]):
                category = "returns"
            elif any(k in query_lower for k in ["payment", "pay", "billing"]):
                category = "payment"
            elif any(k in query_lower for k in ["account", "login", "password"]):
                category = "account"
            elif any(k in query_lower for k in ["product", "item"]):
                category = "product"
            else:
                category = "general"

            return {
                "scenario": "SCENARIO_1_ECOMMERCE",
                "category": category,
                "priority": "medium",
                "reasoning": "Ecommerce keywords detected (fallback classification)"
            }

        # Default to out-of-scope
        return {
            "scenario": "SCENARIO_2_OUT_OF_SCOPE",
            "category": "out_of_scope",
            "priority": "low",
            "reasoning": "No ecommerce or escalation keywords found (fallback classification)"
        }
