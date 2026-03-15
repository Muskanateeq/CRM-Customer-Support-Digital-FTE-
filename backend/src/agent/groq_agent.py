"""
Groq Agent with Tools - Custom implementation for fallback
Provides same functionality as OpenAI agent using Groq's native function calling
"""

import json
import asyncio
from typing import Optional, Dict, Any, List, AsyncIterator
from datetime import datetime

from openai import AsyncOpenAI

from src.config import settings
from src.utils.logging import get_logger
from src.agent.config import get_agent_instructions

# Import database and service functions directly (not decorated versions)
from src.embeddings.vector_search import search_knowledge_base_semantic
from src.database.client import (
    create_ticket as db_create_ticket,
    get_conversation_history,
    create_message,
)

logger = get_logger(__name__)


class GroqAgentWithTools:
    """
    Custom Groq agent implementation with full tool support.
    Uses Groq's native function calling API.
    """

    def __init__(self):
        """Initialize Groq client and tools."""
        self.client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY
        )
        self.model = "llama-3.3-70b-versatile"
        self.tools = self._define_tools()

        # Debug logging
        logger.info(f"Groq agent initialized with model: {self.model}")
        logger.info(f"[DEBUG] Total tools defined: {len(self.tools)}")
        for tool in self.tools:
            logger.info(f"[DEBUG] Tool: {tool['function']['name']}")


    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define tools in Groq-compatible format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Search Custora AI knowledge base for ecommerce information. Use for SCENARIO 1 (supported ecommerce queries) to find relevant articles about orders, shipping, returns, products, account help, or payment methods.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query based on customer's ecommerce question"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_ticket",
                    "description": "Create support ticket to track customer interaction. Use ONLY for SCENARIO 1 (supported ecommerce queries) and SCENARIO 3 (escalation required). DO NOT use for SCENARIO 2 (out-of-scope queries like programming, business advice, unrelated topics). Categories: order_status, shipping, returns, payment, account, product, general.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "enum": ["order_status", "shipping", "returns", "payment", "account", "product", "general"],
                                "description": "Ticket category: order_status (tracking, cancellation), shipping (delivery, international), returns (exchanges, NOT refunds), payment (methods, declined), account (login, profile), product (availability, specs), general (other ecommerce)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "description": "Priority: low (general info), medium (standard support), high (escalation), urgent (refunds, legal, security)",
                                "default": "medium"
                            }
                        },
                        "required": ["category"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_customer_history",
                    "description": "Retrieve conversation history to understand context and avoid asking for information already provided by customer.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of messages to retrieve (default: 10)",
                                "default": 10
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "escalate_to_human",
                    "description": "Escalate to human support team. Use ONLY for SCENARIO 3: refund requests, damaged/wrong/missing items, legal threats, security issues, explicit human request, very angry customers, billing disputes, account locked. DO NOT use for simple questions or out-of-scope queries.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "Clear explanation: refund_request, damaged_item, legal_threat, security_issue, human_requested, customer_angry, billing_dispute, account_locked, privacy_request"
                            },
                            "urgency": {
                                "type": "string",
                                "enum": ["normal", "high", "critical"],
                                "description": "Urgency: normal (standard escalation), high (refunds, damaged items), critical (legal, security, very angry)",
                                "default": "normal"
                            }
                        },
                        "required": ["reason"]
                    }
                }
            }
        ]

    async def run(
        self,
        user_input: str,
        customer_id: str,
        conversation_id: str,
        channel: str = "webform",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run Groq agent with tool support.

        Args:
            user_input: Customer's message
            customer_id: Customer ID (UUID)
            conversation_id: Conversation ID (UUID)
            channel: Communication channel
            context: Additional context

        Returns:
            Dict with final_output and execution metadata
        """
        start_time = datetime.utcnow()

        try:
            logger.info(f"Running Groq agent [cid: {conversation_id[:8]}]")

            # Get channel-specific instructions
            instructions = get_agent_instructions(channel=channel)

            # Prepare context-aware input
            enhanced_input = self._prepare_input(
                user_input, customer_id, conversation_id, channel, context
            )

            # Initialize conversation
            messages = [
                {"role": "system", "content": instructions},
                {"role": "user", "content": enhanced_input}
            ]

            # Tool execution loop (max 5 iterations)
            max_iterations = 5
            final_response = None

            for iteration in range(max_iterations):
                logger.debug(f"Groq iteration {iteration + 1}/{max_iterations}")

                # Call Groq with tools (non-streaming for stability)
                logger.info(f"[DEBUG] Calling Groq API with {len(self.tools)} tools")
                logger.info(f"[DEBUG] Model: {self.model}")
                logger.info(f"[DEBUG] Tools: {[t['function']['name'] for t in self.tools]}")

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=0.7,  # Balanced for natural responses
                    max_tokens=1000
                )

                assistant_message = response.choices[0].message

                # Check if tool calls are needed
                if assistant_message.tool_calls:
                    # Add assistant message to conversation
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in assistant_message.tool_calls
                        ]
                    })

                    # Execute each tool
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        logger.info(f"Executing tool: {tool_name}")

                        # Execute tool
                        tool_result = await self._execute_tool(
                            tool_name,
                            tool_args,
                            customer_id,
                            conversation_id
                        )

                        # Add tool result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(tool_result)
                        })

                    # Continue loop to get next response
                    continue

                else:
                    # No more tools needed, this is the final response
                    final_response = assistant_message.content
                    break

            # If we exhausted iterations without final response
            if final_response is None:
                final_response = "I apologize, but I'm having trouble processing your request. Please try rephrasing your question."

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            logger.info(f"Groq agent completed in {execution_time:.2f}s")

            return {
                "final_output": final_response,
                "execution_time": execution_time,
                "channel": channel,
                "customer_id": customer_id,
                "conversation_id": conversation_id,
                "mode": "groq"
            }

        except Exception as e:
            logger.error(f"Groq agent execution failed: {e}", exc_info=True)
            print(f"[DEBUG] Groq agent error: {type(e).__name__}: {e}", flush=True)
            import traceback
            traceback.print_exc()
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return {
                "final_output": self._get_error_response(channel),
                "error": str(e),
                "execution_time": execution_time,
                "mode": "groq"
            }

    async def run_streamed(
        self,
        user_input: str,
        customer_id: str,
        conversation_id: str,
        channel: str = "webform",
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Run Groq agent with streaming responses.

        Args:
            user_input: Customer's message
            customer_id: Customer ID (UUID)
            conversation_id: Conversation ID (UUID)
            channel: Communication channel
            context: Additional context

        Yields:
            Dict with event type and data (text deltas, tool calls, etc.)
        """
        start_time = datetime.utcnow()

        try:
            logger.info(f"Running Groq agent (streaming) [cid: {conversation_id[:8]}]")

            # Get channel-specific instructions
            instructions = get_agent_instructions(channel=channel)

            # Prepare context-aware input
            enhanced_input = self._prepare_input(
                user_input, customer_id, conversation_id, channel, context
            )

            # Initialize conversation
            messages = [
                {"role": "system", "content": instructions},
                {"role": "user", "content": enhanced_input}
            ]

            # Tool execution loop (max 5 iterations)
            max_iterations = 5
            final_response = ""

            for iteration in range(max_iterations):
                logger.debug(f"Groq streaming iteration {iteration + 1}/{max_iterations}")

                # Call Groq with streaming
                stream = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=0.7,
                    max_tokens=1000,
                    stream=True
                )

                # Collect streaming response
                current_content = ""
                tool_calls_data = []
                current_tool_call = None

                async for chunk in stream:
                    delta = chunk.choices[0].delta

                    # Text content streaming
                    if delta.content:
                        current_content += delta.content
                        yield {
                            "type": "text_delta",
                            "data": delta.content,
                        }

                    # Tool call streaming
                    if delta.tool_calls:
                        for tool_call_chunk in delta.tool_calls:
                            if tool_call_chunk.index is not None:
                                # New tool call
                                if current_tool_call is None or current_tool_call["index"] != tool_call_chunk.index:
                                    if current_tool_call:
                                        tool_calls_data.append(current_tool_call)
                                    current_tool_call = {
                                        "index": tool_call_chunk.index,
                                        "id": tool_call_chunk.id or "",
                                        "type": "function",
                                        "function": {
                                            "name": tool_call_chunk.function.name or "",
                                            "arguments": tool_call_chunk.function.arguments or ""
                                        }
                                    }
                                else:
                                    # Continue existing tool call
                                    if tool_call_chunk.function.name:
                                        current_tool_call["function"]["name"] += tool_call_chunk.function.name
                                    if tool_call_chunk.function.arguments:
                                        current_tool_call["function"]["arguments"] += tool_call_chunk.function.arguments

                # Add last tool call if exists
                if current_tool_call:
                    tool_calls_data.append(current_tool_call)

                # Check if tool calls are needed
                if tool_calls_data:
                    # Add assistant message to conversation
                    messages.append({
                        "role": "assistant",
                        "content": current_content or "",
                        "tool_calls": [
                            {
                                "id": tc["id"],
                                "type": "function",
                                "function": {
                                    "name": tc["function"]["name"],
                                    "arguments": tc["function"]["arguments"]
                                }
                            }
                            for tc in tool_calls_data
                        ]
                    })

                    # Execute each tool
                    for tool_call in tool_calls_data:
                        tool_name = tool_call["function"]["name"]
                        tool_args = json.loads(tool_call["function"]["arguments"])

                        logger.info(f"Executing tool: {tool_name}")

                        # Yield tool call event
                        yield {
                            "type": "tool_call",
                            "data": {
                                "tool_name": tool_name,
                                "tool_id": tool_call["id"],
                            },
                        }

                        # Execute tool
                        tool_result = await self._execute_tool(
                            tool_name,
                            tool_args,
                            customer_id,
                            conversation_id
                        )

                        # Yield tool output event
                        yield {
                            "type": "tool_output",
                            "data": {
                                "output": tool_result,
                            },
                        }

                        # Add tool result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": str(tool_result)
                        })

                    # Continue loop to get next response
                    continue

                else:
                    # No more tools needed, this is the final response
                    final_response = current_content
                    break

            # If we exhausted iterations without final response
            if not final_response:
                final_response = "I apologize, but I'm having trouble processing your request. Please try rephrasing your question."

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            # Yield final event
            yield {
                "type": "final",
                "data": {
                    "final_output": final_response,
                    "execution_time": execution_time,
                },
            }

            logger.info(f"Groq agent streaming completed in {execution_time:.2f}s")

        except Exception as e:
            logger.error(f"Groq agent streaming failed: {e}", exc_info=True)
            yield {
                "type": "error",
                "data": {
                    "error": str(e),
                    "fallback_response": self._get_error_response(channel),
                },
            }

    async def _execute_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        customer_id: str,
        conversation_id: str
    ) -> str:
        """Execute a tool function using plain async implementations."""
        try:
            if tool_name == "search_knowledge_base":
                # Search knowledge base
                query = tool_args.get("query", "")
                limit = tool_args.get("limit", 5)

                results = await search_knowledge_base_semantic(
                    query=query,
                    limit=limit
                )

                if not results:
                    return "No relevant articles found in the knowledge base."

                # Format results
                formatted = "Here are relevant articles from our knowledge base:\n\n"
                for i, result in enumerate(results, 1):
                    formatted += f"{i}. **{result.get('title', 'Untitled')}**\n"
                    formatted += f"   {result.get('content', '')[:200]}...\n\n"

                return formatted

            elif tool_name == "create_ticket":
                # Create support ticket
                category = tool_args.get("category", "general")
                priority = tool_args.get("priority", "medium")

                ticket_id = await db_create_ticket(
                    customer_id=customer_id,
                    conversation_id=conversation_id,
                    category=category,
                    priority=priority,
                    source_channel="webform",
                    resolution_notes=None
                )

                return f"✓ Support ticket created successfully!\nTicket ID: #{ticket_id}\nCategory: {category}\nPriority: {priority}\nOur team will review and respond soon."

            elif tool_name == "get_customer_history":
                # Get conversation history
                limit = tool_args.get("limit", 10)

                history = await get_conversation_history(
                    conversation_id=conversation_id,
                    limit=limit
                )

                if not history:
                    return "No previous conversation history found."

                # Format history
                formatted = "Previous conversation:\n\n"
                for msg in history:
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    formatted += f"[{role.upper()}]: {content}\n\n"

                return formatted

            elif tool_name == "escalate_to_human":
                # Escalate to human agent
                reason = tool_args.get("reason", "Customer requested human support")
                urgency = tool_args.get("urgency", "normal")

                # Create escalation ticket
                priority_map = {
                    "normal": "medium",
                    "high": "high",
                    "critical": "urgent"
                }

                ticket_id = await db_create_ticket(
                    customer_id=customer_id,
                    conversation_id=conversation_id,
                    category="general",
                    priority=priority_map.get(urgency, "medium"),
                    source_channel="webform",
                    resolution_notes=f"ESCALATION: {reason}"
                )

                return f"✓ Escalated to human support team.\nTicket ID: #{ticket_id}\nUrgency: {urgency}\nReason: {reason}\nA support agent will contact you shortly."

            else:
                return f"Unknown tool: {tool_name}"

        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name} - {e}", exc_info=True)
            return f"Error executing {tool_name}: {str(e)}"

    def _prepare_input(
        self,
        user_input: str,
        customer_id: str,
        conversation_id: str,
        channel: str,
        context: Optional[Dict[str, Any]],
    ) -> str:
        """Prepare enhanced input with context."""
        context_parts = [
            f"[CONTEXT]",
            f"Customer ID: {customer_id}",
            f"Conversation ID: {conversation_id}",
            f"Channel: {channel.upper()}",
        ]

        if context and "sentiment" in context:
            context_parts.append(f"Sentiment: {context['sentiment']}")

        if context and "metadata" in context:
            for key, value in context["metadata"].items():
                context_parts.append(f"{key}: {value}")

        context_parts.append("[/CONTEXT]\n")

        return "\n".join(context_parts) + f"\nCustomer Message:\n{user_input}"

    def _get_error_response(self, channel: str) -> str:
        """Get channel-appropriate error response."""
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
