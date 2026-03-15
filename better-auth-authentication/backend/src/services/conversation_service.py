"""
Conversation Service Layer

Business logic for conversation operations including:
- CRUD operations for conversations
- Message management
- Ownership validation
- Pagination
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_, func, desc
from fastapi import HTTPException, status

from src.models.conversation import Conversation, ConversationPublic, ConversationList
from src.models.message import Message, MessagePublic, MessageCreate, MessageList


class ConversationService:
    """Service class for conversation operations"""

    @staticmethod
    async def create_conversation(
        user_id: str,
        session: AsyncSession
    ) -> ConversationPublic:
        """
        Create a new conversation for the user.

        Args:
            user_id: User ID from JWT token
            session: Database session

        Returns:
            Created conversation
        """
        conversation = Conversation(user_id=user_id)

        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

        return ConversationPublic(
            id=conversation.id,
            user_id=conversation.user_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=0
        )

    @staticmethod
    async def get_user_conversations(
        user_id: str,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0
    ) -> ConversationList:
        """
        Get all conversations for a user with message counts.

        Args:
            user_id: User ID from JWT token
            session: Database session
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            List of conversations with message counts
        """
        # Get conversations with message counts
        query = (
            select(
                Conversation,
                func.count(Message.id).label('message_count')
            )
            .outerjoin(Message, Message.conversation_id == Conversation.id)
            .where(Conversation.user_id == user_id)
            .group_by(Conversation.id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .offset(offset)
        )

        result = await session.execute(query)
        rows = result.all()

        conversations = [
            ConversationPublic(
                id=conv.id,
                user_id=conv.user_id,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=msg_count
            )
            for conv, msg_count in rows
        ]

        # Get total count
        count_query = select(func.count(Conversation.id)).where(
            Conversation.user_id == user_id
        )
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        return ConversationList(
            conversations=conversations,
            total=total
        )

    @staticmethod
    async def get_conversation(
        conversation_id: int,
        user_id: str,
        session: AsyncSession
    ) -> ConversationPublic:
        """
        Get a conversation by ID with ownership validation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID from JWT token
            session: Database session

        Returns:
            Conversation with message count

        Raises:
            HTTPException: If conversation not found or access denied
        """
        # Get conversation with message count
        query = (
            select(
                Conversation,
                func.count(Message.id).label('message_count')
            )
            .outerjoin(Message, Message.conversation_id == Conversation.id)
            .where(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
            )
            .group_by(Conversation.id)
        )

        result = await session.execute(query)
        row = result.first()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        conv, msg_count = row

        return ConversationPublic(
            id=conv.id,
            user_id=conv.user_id,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=msg_count
        )

    @staticmethod
    async def delete_conversation(
        conversation_id: int,
        user_id: str,
        session: AsyncSession
    ) -> None:
        """
        Delete a conversation with ownership validation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID from JWT token
            session: Database session

        Raises:
            HTTPException: If conversation not found or access denied
        """
        # Verify ownership
        query = select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        result = await session.execute(query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Delete conversation (messages will cascade)
        await session.delete(conversation)
        await session.commit()

    @staticmethod
    async def get_conversation_messages(
        conversation_id: int,
        user_id: str,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0
    ) -> MessageList:
        """
        Get messages for a conversation with pagination.

        Args:
            conversation_id: Conversation ID
            user_id: User ID from JWT token
            session: Database session
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List of messages with pagination info

        Raises:
            HTTPException: If conversation not found or access denied
        """
        # Verify conversation ownership
        conv_query = select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        conv_result = await session.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Get messages
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(limit)
            .offset(offset)
        )

        result = await session.execute(query)
        messages = result.scalars().all()

        # Get total count
        count_query = select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        message_list = [
            MessagePublic(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at
            )
            for msg in messages
        ]

        return MessageList(
            messages=message_list,
            total=total,
            has_more=(offset + len(message_list)) < total
        )

    @staticmethod
    async def add_message(
        conversation_id: int,
        user_id: str,
        message_data: MessageCreate,
        session: AsyncSession
    ) -> MessagePublic:
        """
        Add a message to a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID from JWT token
            message_data: Message creation data
            session: Database session

        Returns:
            Created message

        Raises:
            HTTPException: If conversation not found or access denied
        """
        # Verify conversation ownership
        conv_query = select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        conv_result = await session.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Create message
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=message_data.role,
            content=message_data.content
        )

        session.add(message)

        # Update conversation updated_at
        conversation.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(message)

        return MessagePublic(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at
        )
