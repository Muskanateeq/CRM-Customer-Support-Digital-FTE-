"""
Admin API - Knowledge Base Management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.embeddings.vector_search import insert_knowledge_base_article
from src.database.client import update_ticket_status, get_ticket

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


class KnowledgeBaseArticle(BaseModel):
    title: str
    content: str
    category: str


class TicketResolution(BaseModel):
    ticket_id: str
    resolution_notes: str
    create_kb_article: bool = False
    kb_article_title: Optional[str] = None
    kb_article_category: Optional[str] = None


@router.post("/knowledge-base/articles")
async def create_knowledge_article(article: KnowledgeBaseArticle):
    """
    Create new knowledge base article with automatic embedding generation.
    
    Usage:
    POST /api/v1/admin/knowledge-base/articles
    {
        "title": "How to Create Landing Pages",
        "content": "Step by step guide...",
        "category": "tutorials"
    }
    """
    try:
        article_id = await insert_knowledge_base_article(
            title=article.title,
            content=article.content,
            category=article.category,
            generate_embedding=True
        )
        
        return {
            "success": True,
            "article_id": article_id,
            "message": "Article created successfully with embeddings"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickets/resolve")
async def resolve_ticket(resolution: TicketResolution):
    """
    Resolve ticket and optionally create knowledge base article.
    
    Usage:
    POST /api/v1/admin/tickets/resolve
    {
        "ticket_id": "uuid",
        "resolution_notes": "Here's how to solve...",
        "create_kb_article": true,
        "kb_article_title": "How to...",
        "kb_article_category": "tutorials"
    }
    """
    try:
        # Get ticket details
        ticket = await get_ticket(resolution.ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Update ticket status
        await update_ticket_status(
            ticket_id=resolution.ticket_id,
            status="resolved",
            resolution_notes=resolution.resolution_notes
        )
        
        result = {
            "success": True,
            "ticket_id": resolution.ticket_id,
            "message": "Ticket resolved successfully"
        }
        
        # Create KB article if requested
        if resolution.create_kb_article:
            article_id = await insert_knowledge_base_article(
                title=resolution.kb_article_title or f"Solution for Ticket #{resolution.ticket_id}",
                content=resolution.resolution_notes,
                category=resolution.kb_article_category or "general",
                generate_embedding=True
            )
            result["kb_article_id"] = article_id
            result["message"] += " and knowledge base article created"
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
