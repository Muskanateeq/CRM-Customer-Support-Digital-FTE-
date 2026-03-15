"""
Chat Service Layer - Smart Chatbot with MCP Integration

Orchestrates AI chat functionality using:
- TaskNestAgent (OpenAI GPT-4o with smart instructions)
- MCP Server (Official MCP SDK for tool definitions)
- Smart Parser (Natural language understanding)
- Conversation persistence
- Streaming responses
"""

import json
import logging
from typing import List, Dict, Any, Optional, AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.agents.tasknest_agent import get_agent
from src.mcp.tools import execute_tool
from src.services.conversation_service import ConversationService
from src.models.message import MessageCreate

# Configure logging
logger = logging.getLogger(__name__)


class ChatService:
    """Service class for AI chat operations"""

    @staticmethod
    async def send_message_stream(
        user_id: str,
        conversation_id: Optional[int],
        user_message: str,
        session: AsyncSession
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Process a user message and stream AI response in real-time using TaskNestAgent.

        Yields events:
        - {"type": "conversation_id", "conversation_id": int}
        - {"type": "content", "content": str}
        - {"type": "tool_call", "tool": str, "status": str}
        - {"type": "done", "message_id": int}
        - {"type": "error", "error": str}

        Args:
            user_id: User ID from JWT token
            conversation_id: Optional conversation ID (creates new if None)
            user_message: User's message text
            session: Database session

        Yields:
            Event dictionaries for SSE streaming
        """
        try:
            # Step 1: Get or create conversation
            if conversation_id is None:
                conversation = await ConversationService.create_conversation(user_id, session)
                conversation_id = conversation.id
            else:
                conversation = await ConversationService.get_conversation(
                    conversation_id, user_id, session
                )

            # Yield conversation ID first
            yield {"type": "conversation_id", "conversation_id": conversation_id}

            # Step 2: Save user message
            await ConversationService.add_message(
                conversation_id=conversation_id,
                user_id=user_id,
                message_data=MessageCreate(
                    conversation_id=conversation_id,
                    role="user",
                    content=user_message
                ),
                session=session
            )

            # Step 3: Build message history with agent's system instructions
            message_history = await ChatService._build_message_history(
                conversation_id, user_id, session
            )

            # Step 4: Get MCP tools (from src/mcp/tools.py)
            from src.mcp.tools import get_all_tools
            tools = get_all_tools()

            # Step 5: Stream agent response
            accumulated_content = ""
            tool_calls_data = None

            agent = get_agent()
            stream = await agent.create_completion(
                messages=message_history,
                tools=tools,
                stream=True
            )

            async for chunk in stream:
                # Extract content from chunk
                if chunk.choices:
                    choice = chunk.choices[0]
                    delta = choice.delta

                    # Stream content
                    if delta.content:
                        content = delta.content
                        accumulated_content += content
                        yield {"type": "content", "content": content}

                    # Check for tool calls
                    if delta.tool_calls:
                        tool_calls_data = delta.tool_calls

            # Step 6: Handle tool calls if present
            tool_results = []
            if tool_calls_data:
                for tool_call in tool_calls_data:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Notify about tool execution
                    yield {
                        "type": "tool_call",
                        "tool": function_name,
                        "status": "executing"
                    }

                    # Execute tool
                    try:
                        result = await execute_tool(
                            tool_name=function_name,
                            arguments=function_args,
                            user_id=user_id,
                            session=session
                        )
                        tool_results.append({
                            "tool": function_name,
                            "arguments": function_args,
                            "result": result
                        })
                        yield {
                            "type": "tool_call",
                            "tool": function_name,
                            "status": "completed"
                        }
                    except Exception as e:
                        logger.error(f"Tool execution failed: {e}")
                        yield {
                            "type": "tool_call",
                            "tool": function_name,
                            "status": "failed",
                            "error": str(e)
                        }

                # If tools were executed, get final response
                if tool_results:
                    # Convert tool_calls_data to dict format for message history
                    tool_calls_dict = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in tool_calls_data
                    ]

                    message_history.append({
                        "role": "assistant",
                        "content": accumulated_content or None,
                        "tool_calls": tool_calls_dict
                    })

                    for tool_result in tool_results:
                        message_history.append({
                            "role": "tool",
                            "tool_call_id": tool_calls_dict[0]["id"],
                            "name": tool_result["tool"],
                            "content": json.dumps(tool_result.get("result"))
                        })

                    # Stream final response
                    accumulated_content = ""
                    agent = get_agent()
                    stream = await agent.create_completion(
                        messages=message_history,
                        tools=tools,
                        stream=True
                    )

                    async for chunk in stream:
                        if chunk.choices:
                            choice = chunk.choices[0]
                            delta = choice.delta
                            if delta.content:
                                content = delta.content
                                accumulated_content += content
                                yield {"type": "content", "content": content}

            # Step 7: Save assistant response
            final_content = accumulated_content or "Done!"
            assistant_msg = await ConversationService.add_message(
                conversation_id=conversation_id,
                user_id=user_id,
                message_data=MessageCreate(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=final_content
                ),
                session=session
            )

            # Step 8: Send done event
            yield {
                "type": "done",
                "message_id": assistant_msg.id,
                "tool_calls": tool_results if tool_results else None
            }

        except Exception as e:
            logger.error(f"[ChatService] Streaming error: {e}", exc_info=True)
            yield {"type": "error", "error": str(e)}

    @staticmethod
    async def send_message(
        user_id: str,
        conversation_id: Optional[int],
        user_message: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Process a user message and generate AI response using TaskNestAgent.

        This method:
        1. Creates/retrieves conversation
        2. Saves user message
        3. Builds message history with agent instructions
        4. Calls agent with MCP tools
        5. Executes tool calls if needed
        6. Saves assistant response
        7. Returns complete response

        Args:
            user_id: User ID from JWT token
            conversation_id: Optional conversation ID (creates new if None)
            user_message: User's message text
            session: Database session

        Returns:
            {
                "conversation_id": int,
                "message": str,  # Assistant's response
                "tool_calls": [...],  # Optional tool executions
                "created_at": datetime
            }

        Raises:
            HTTPException: If conversation not found or access denied
        """
        # Step 1: Get or create conversation
        if conversation_id is None:
            conversation = await ConversationService.create_conversation(user_id, session)
            conversation_id = conversation.id
        else:
            # Verify conversation exists and belongs to user
            conversation = await ConversationService.get_conversation(
                conversation_id, user_id, session
            )

        # Step 2: Save user message
        user_msg = await ConversationService.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            message_data=MessageCreate(
                conversation_id=conversation_id,
                role="user",
                content=user_message
            ),
            session=session
        )

        # Step 3: Build message history with agent's system instructions
        message_history = await ChatService._build_message_history(
            conversation_id, user_id, session
        )

        # Step 4: Get MCP tools
        from src.mcp.tools import get_all_tools
        tools = get_all_tools()

        # Step 5: Call agent
        try:
            logger.info(f"[ChatService] Calling agent with {len(message_history)} messages and {len(tools)} tools")
            agent = get_agent()
            response = await agent.create_completion(
                messages=message_history,
                tools=tools,
                stream=False
            )
            logger.info(f"[ChatService] Agent call successful")
        except Exception as e:
            logger.error(f"[ChatService] Agent call failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent call failed: {str(e)}"
            )

        # Step 6: Process response and handle tool calls
        try:
            assistant_message = response.choices[0].message
        except (AttributeError, IndexError) as e:
            logger.error(f"[ChatService] Invalid agent response format: {e}", exc_info=True)
            logger.error(f"[ChatService] Agent response: {response}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid agent response format: {str(e)}"
            )

        tool_results = []

        # Check if agent wants to call tools
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Execute tool
                try:
                    result = await execute_tool(
                        tool_name=function_name,
                        arguments=function_args,
                        user_id=user_id,
                        session=session
                    )
                    tool_results.append({
                        "tool": function_name,
                        "arguments": function_args,
                        "result": result
                    })
                except Exception as e:
                    tool_results.append({
                        "tool": function_name,
                        "arguments": function_args,
                        "error": str(e)
                    })

            # If tools were called, make another agent call with results
            if tool_results:
                # Convert tool_calls to dict format for message history
                tool_calls_dict = [
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

                # Add assistant message with tool calls
                message_history.append({
                    "role": "assistant",
                    "content": assistant_message.content or None,
                    "tool_calls": tool_calls_dict
                })

                # Add tool results as separate messages
                for i, tool_result in enumerate(tool_results):
                    message_history.append({
                        "role": "tool",
                        "tool_call_id": tool_calls_dict[i]["id"],
                        "name": tool_result["tool"],
                        "content": json.dumps(tool_result.get("result", tool_result.get("error")))
                    })

                # Call agent again to generate final response
                agent = get_agent()
                final_response = await agent.create_completion(
                    messages=message_history,
                    tools=tools,
                    stream=False
                )
                assistant_message = final_response.choices[0].message

        # Step 7: Save assistant response
        assistant_content = assistant_message.content or "Done!"
        assistant_msg = await ConversationService.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            message_data=MessageCreate(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_content
            ),
            session=session
        )

        # Step 8: Return response
        return {
            "conversation_id": conversation_id,
            "message": assistant_content,
            "tool_calls": tool_results if tool_results else None,
            "created_at": assistant_msg.created_at
        }

    @staticmethod
    async def _build_message_history(
        conversation_id: int,
        user_id: str,
        session: AsyncSession,
        max_messages: int = 20
    ) -> List[Dict[str, str]]:
        """
        Build message history for agent context.

        Args:
            conversation_id: Conversation ID
            user_id: User ID from JWT token
            session: Database session
            max_messages: Maximum number of messages to include

        Returns:
            List of messages in OpenAI format with agent's system instructions
        """
        # Get recent messages
        message_list = await ConversationService.get_conversation_messages(
            conversation_id=conversation_id,
            user_id=user_id,
            session=session,
            limit=max_messages,
            offset=0
        )

        # Build message history with agent's system instructions
        agent = get_agent()
        messages = [
            {
                "role": "system",
                "content": agent.get_system_instructions()
            }
        ]

        # Add conversation messages
        for msg in message_list.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        return messages

    @staticmethod
    async def get_conversation_history(
        conversation_id: int,
        user_id: str,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get conversation history with messages.

        Args:
            conversation_id: Conversation ID
            user_id: User ID from JWT token
            session: Database session
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            {
                "conversation": ConversationPublic,
                "messages": [MessagePublic, ...],
                "total": int,
                "has_more": bool
            }
        """
        # Get conversation
        conversation = await ConversationService.get_conversation(
            conversation_id, user_id, session
        )

        # Get messages
        message_list = await ConversationService.get_conversation_messages(
            conversation_id, user_id, session, limit, offset
        )

        return {
            "conversation": conversation,
            "messages": message_list.messages,
            "total": message_list.total,
            "has_more": message_list.has_more
        }

    @staticmethod
    async def list_conversations(
        user_id: str,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List all conversations for a user.

        Args:
            user_id: User ID from JWT token
            session: Database session
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            {
                "conversations": [ConversationPublic, ...],
                "total": int
            }
        """
        conversation_list = await ConversationService.get_user_conversations(
            user_id, session, limit, offset
        )

        return {
            "conversations": conversation_list.conversations,
            "total": conversation_list.total
        }

    @staticmethod
    async def delete_conversation(
        conversation_id: int,
        user_id: str,
        session: AsyncSession
    ) -> None:
        """
        Delete a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID from JWT token
            session: Database session
        """
        await ConversationService.delete_conversation(
            conversation_id, user_id, session
        )
