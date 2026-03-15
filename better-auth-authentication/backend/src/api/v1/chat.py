"""
Chat API Router

Endpoints for AI chat functionality:
- Send messages and get AI responses (streaming and non-streaming)
- Manage conversations
- View conversation history
"""

import json
import logging
from typing import Optional, AsyncIterator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from src.database import get_session
from src.api.deps import get_current_user_id
from src.services.chat_service import ChatService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for sending a chat message"""
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    conversation_id: Optional[int] = Field(None, description="Optional conversation ID (creates new if not provided)")


class ChatResponse(BaseModel):
    """Response model for chat message"""
    conversation_id: int
    message: str
    tool_calls: Optional[list] = None
    created_at: str


class ConversationListResponse(BaseModel):
    """Response model for conversation list"""
    conversations: list
    total: int


class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history"""
    conversation: dict
    messages: list
    total: int
    has_more: bool


# Endpoints
@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_chat_message(
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Send a message to the AI assistant.

    This endpoint:
    - Creates a new conversation if conversation_id is not provided
    - Processes the message with the LLM
    - Executes any tool calls (task operations)
    - Returns the AI response

    **Example Request:**
    ```json
    {
        "message": "Add a task to buy groceries tomorrow",
        "conversation_id": null
    }
    ```

    **Example Response:**
    ```json
    {
        "conversation_id": 1,
        "message": "I've created a task 'Buy groceries' with due date tomorrow.",
        "tool_calls": [
            {
                "tool": "create_task",
                "arguments": {"title": "Buy groceries", "due_date": "2024-01-15"},
                "result": {"success": true, "task": {...}}
            }
        ],
        "created_at": "2024-01-14T10:30:00Z"
    }
    ```
    """
    try:
        result = await ChatService.send_message(
            user_id=user_id,
            conversation_id=request.conversation_id,
            user_message=request.message,
            session=session
        )

        return ChatResponse(
            conversation_id=result["conversation_id"],
            message=result["message"],
            tool_calls=result.get("tool_calls"),
            created_at=result["created_at"].isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ChatAPI] Failed to process message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.post("/stream")
async def send_chat_message_stream(
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Send a message to the AI assistant with streaming response.

    Returns Server-Sent Events (SSE) stream with real-time AI response.

    **Event Types:**
    - `conversation_id`: Initial event with conversation ID
    - `content`: Streaming text chunks from AI
    - `tool_call`: Tool execution events
    - `done`: Final event when complete
    - `error`: Error event if something fails
    """
    async def event_generator() -> AsyncIterator[str]:
        try:
            async for event in ChatService.send_message_stream(
                user_id=user_id,
                conversation_id=request.conversation_id,
                user_message=request.message,
                session=session
            ):
                # Send SSE formatted event
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.error(f"[ChatAPI] Streaming error: {e}", exc_info=True)
            error_event = {
                "type": "error",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all conversations for the current user.

    **Query Parameters:**
    - limit: Maximum number of conversations to return (default: 50)
    - offset: Number of conversations to skip (default: 0)

    **Example Response:**
    ```json
    {
        "conversations": [
            {
                "id": 1,
                "user_id": "user-123",
                "created_at": "2024-01-14T10:00:00Z",
                "updated_at": "2024-01-14T10:30:00Z",
                "message_count": 5
            }
        ],
        "total": 10
    }
    ```
    """
    try:
        result = await ChatService.list_conversations(
            user_id=user_id,
            session=session,
            limit=limit,
            offset=offset
        )

        return ConversationListResponse(
            conversations=[conv.model_dump() for conv in result["conversations"]],
            total=result["total"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list conversations: {str(e)}"
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: int,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get a conversation with its message history.

    **Path Parameters:**
    - conversation_id: The conversation ID

    **Query Parameters:**
    - limit: Maximum number of messages to return (default: 50)
    - offset: Number of messages to skip (default: 0)

    **Example Response:**
    ```json
    {
        "conversation": {
            "id": 1,
            "user_id": "user-123",
            "created_at": "2024-01-14T10:00:00Z",
            "updated_at": "2024-01-14T10:30:00Z",
            "message_count": 5
        },
        "messages": [
            {
                "id": 1,
                "conversation_id": 1,
                "role": "user",
                "content": "Add a task to buy groceries",
                "created_at": "2024-01-14T10:00:00Z"
            },
            {
                "id": 2,
                "conversation_id": 1,
                "role": "assistant",
                "content": "I've created the task for you.",
                "created_at": "2024-01-14T10:00:05Z"
            }
        ],
        "total": 5,
        "has_more": false
    }
    ```
    """
    try:
        result = await ChatService.get_conversation_history(
            conversation_id=conversation_id,
            user_id=user_id,
            session=session,
            limit=limit,
            offset=offset
        )

        return ConversationHistoryResponse(
            conversation=result["conversation"].model_dump(),
            messages=[msg.model_dump() for msg in result["messages"]],
            total=result["total"],
            has_more=result["has_more"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a conversation and all its messages.

    **Path Parameters:**
    - conversation_id: The conversation ID

    **Response:**
    - 204 No Content on success
    - 404 Not Found if conversation doesn't exist or doesn't belong to user
    """
    try:
        await ChatService.delete_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            session=session
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}"
        )
