"""
MCP Server for TaskNest Smart Chatbot

This server exposes all TaskNest operations as MCP tools using the Official MCP SDK.
The OpenAI Agent will automatically discover and use these tools.

Tools:
- create_task: Create tasks with smart parsing
- list_tasks: Search and filter tasks
- update_task: Modify task details
- complete_task: Mark tasks as done/undone
- delete_task: Remove tasks
- create_tag: Create new tags
- list_tags: View all tags
- search_tasks: Advanced search
"""

import asyncio
import sys
import os
from typing import Optional, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mcp.server import Server
from mcp.types import Tool, TextContent
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.services.task_service import TaskService
from src.services.tag_service import TagService
from src.models.task import TaskCreate, TaskUpdate, TaskCompletionToggle
from src.models.tag import TagCreate as TagCreateModel
from src.utils.smart_parser import SmartParser


# Create MCP server
server = Server("tasknest-mcp")


@server.tool()
async def create_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = "medium",
    due_date: Optional[str] = None,
    due_time: Optional[str] = None,
    tag_names: Optional[List[str]] = None,
    recurrence_pattern: Optional[str] = None
) -> dict:
    """
    Create a new task with intelligent parsing.

    This tool automatically handles:
    - Date parsing (26-02-2026, tomorrow, kal, next week)
    - Priority parsing (high, urgent, zaruri)
    - Tag creation (auto-creates if doesn't exist)
    - Time parsing (2pm, 14:00, do baje)

    Args:
        user_id: User ID from authentication
        title: Task title (required)
        description: Optional task description
        priority: Priority level (high/medium/low) - supports English & Urdu
        due_date: Due date in any format
        due_time: Due time in any format
        tag_names: List of tag names (will be created if don't exist)
        recurrence_pattern: daily, weekly, or monthly

    Returns:
        Success status and created task details

    Examples:
        - "Create task: meeting tomorrow at 2pm, high priority"
        - "kal ka meeting task banao 2 baje, zaruri hai"
    """
    async for session in get_session():
        try:
            # Smart parsing
            if due_date:
                parsed_date = SmartParser.parse_date(due_date)
                if parsed_date:
                    due_date = parsed_date

            if due_time:
                parsed_time = SmartParser.parse_time(due_time)
                if parsed_time:
                    due_time = parsed_time

            if priority:
                priority = SmartParser.parse_priority(priority)

            # Resolve tags
            tag_ids = []
            if tag_names:
                tag_ids = await SmartParser.resolve_tags(user_id, tag_names, session)

            # Create task
            task_data = TaskCreate(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                due_time=due_time,
                recurrence_pattern=recurrence_pattern,
                tag_ids=tag_ids
            )

            result = await TaskService.create_task(user_id, task_data, session)

            return {
                "success": True,
                "task": {
                    "id": result.id,
                    "title": result.title,
                    "description": result.description,
                    "priority": result.priority,
                    "due_date": str(result.due_date) if result.due_date else None,
                    "due_time": str(result.due_time) if result.due_time else None,
                    "completed": result.completed,
                    "tags": [{"id": t.id, "name": t.name} for t in result.tags]
                },
                "message": f"Task '{result.title}' created successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create task: {str(e)}"
            }
        finally:
            break


@server.tool()
async def list_tasks(
    user_id: str,
    search: Optional[str] = None,
    status: Optional[str] = "all",
    priority: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    limit: Optional[int] = 50
) -> dict:
    """
    List and search user's tasks.

    Args:
        user_id: User ID from authentication
        search: Search query for title/description
        status: Filter by status (all/active/completed)
        priority: Filter by priority (high/medium/low)
        sort_by: Sort field (created_at/due_date/priority/title)
        sort_order: Sort order (asc/desc)
        limit: Maximum number of tasks to return

    Returns:
        List of tasks matching criteria

    Examples:
        - "Show me my tasks"
        - "List high priority tasks"
        - "Search for meeting tasks"
    """
    async for session in get_session():
        try:
            tasks = await TaskService.get_user_tasks(
                user_id=user_id,
                session=session,
                search=search,
                status=status,
                priority=priority,
                sort_by=sort_by,
                sort_order=sort_order,
                limit=limit
            )

            return {
                "success": True,
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "priority": t.priority,
                        "due_date": str(t.due_date) if t.due_date else None,
                        "completed": t.completed,
                        "tags": [{"id": tag.id, "name": tag.name} for tag in t.tags]
                    }
                    for t in tasks
                ],
                "count": len(tasks),
                "message": f"Found {len(tasks)} task(s)"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list tasks: {str(e)}"
            }
        finally:
            break


@server.tool()
async def complete_task(
    user_id: str,
    task_id: int,
    completed: bool = True
) -> dict:
    """
    Mark a task as complete or incomplete.

    Args:
        user_id: User ID from authentication
        task_id: Task ID (numeric)
        completed: True to mark complete, False to mark incomplete

    Returns:
        Success status and updated task

    Examples:
        - "Complete task 5"
        - "Mark task 10 as done"
        - "Uncomplete task 3"
    """
    async for session in get_session():
        try:
            result = await TaskService.toggle_completion(
                task_id=task_id,
                user_id=user_id,
                completed=completed,
                session=session
            )

            if not result:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"Task {task_id} not found or access denied"
                }

            status = "completed" if completed else "incomplete"
            return {
                "success": True,
                "task": {
                    "id": result.id,
                    "title": result.title,
                    "completed": result.completed
                },
                "message": f"Task '{result.title}' marked as {status}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to complete task: {str(e)}"
            }
        finally:
            break


@server.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    due_time: Optional[str] = None
) -> dict:
    """
    Update task details.

    Args:
        user_id: User ID from authentication
        task_id: Task ID to update
        title: New title
        description: New description
        priority: New priority (with smart parsing)
        due_date: New due date (with smart parsing)
        due_time: New due time (with smart parsing)

    Returns:
        Success status and updated task

    Examples:
        - "Update task 5 priority to high"
        - "Change task 3 due date to tomorrow"
    """
    async for session in get_session():
        try:
            # Smart parsing
            if due_date:
                parsed_date = SmartParser.parse_date(due_date)
                if parsed_date:
                    due_date = parsed_date

            if due_time:
                parsed_time = SmartParser.parse_time(due_time)
                if parsed_time:
                    due_time = parsed_time

            if priority:
                priority = SmartParser.parse_priority(priority)

            # Build update data
            update_data = TaskUpdate(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                due_time=due_time
            )

            result = await TaskService.update_task(
                task_id=task_id,
                user_id=user_id,
                task_data=update_data,
                session=session
            )

            if not result:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"Task {task_id} not found or access denied"
                }

            return {
                "success": True,
                "task": {
                    "id": result.id,
                    "title": result.title,
                    "priority": result.priority,
                    "due_date": str(result.due_date) if result.due_date else None
                },
                "message": f"Task '{result.title}' updated successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update task: {str(e)}"
            }
        finally:
            break


@server.tool()
async def delete_task(
    user_id: str,
    task_id: int
) -> dict:
    """
    Delete a task permanently.

    Args:
        user_id: User ID from authentication
        task_id: Task ID to delete

    Returns:
        Success status

    Examples:
        - "Delete task 5"
        - "Remove task 10"
    """
    async for session in get_session():
        try:
            await TaskService.delete_task(
                task_id=task_id,
                user_id=user_id,
                session=session
            )

            return {
                "success": True,
                "message": f"Task {task_id} deleted successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete task: {str(e)}"
            }
        finally:
            break


@server.tool()
async def list_tags(user_id: str) -> dict:
    """
    List all user's tags.

    Args:
        user_id: User ID from authentication

    Returns:
        List of all tags

    Examples:
        - "Show my tags"
        - "List all tags"
    """
    async for session in get_session():
        try:
            tags = await TagService.get_user_tags(
                user_id=user_id,
                session=session
            )

            return {
                "success": True,
                "tags": [
                    {"id": t.id, "name": t.name}
                    for t in tags
                ],
                "count": len(tags),
                "message": f"Found {len(tags)} tag(s)"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list tags: {str(e)}"
            }
        finally:
            break


@server.tool()
async def create_tag(
    user_id: str,
    name: str
) -> dict:
    """
    Create a new tag.

    Args:
        user_id: User ID from authentication
        name: Tag name

    Returns:
        Success status and created tag

    Examples:
        - "Create a tag called 'urgent'"
        - "Add new tag 'work'"
    """
    async for session in get_session():
        try:
            tag_data = TagCreateModel(name=name)
            result = await TagService.create_tag(
                user_id=user_id,
                tag_data=tag_data,
                session=session
            )

            if not result:
                return {
                    "success": False,
                    "error": "Tag already exists",
                    "message": f"Tag '{name}' already exists"
                }

            return {
                "success": True,
                "tag": {"id": result.id, "name": result.name},
                "message": f"Tag '{result.name}' created successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create tag: {str(e)}"
            }
        finally:
            break


@server.tool()
async def delete_tag(
    user_id: str,
    tag_id: int
) -> dict:
    """
    Delete a tag.

    Args:
        user_id: User ID from authentication
        tag_id: Tag ID to delete

    Returns:
        Success status

    Examples:
        - "Delete tag 5"
        - "Remove the urgent tag"
    """
    async for session in get_session():
        try:
            result = await TagService.delete_tag(
                tag_id=tag_id,
                user_id=user_id,
                session=session
            )

            if not result:
                return {
                    "success": False,
                    "error": "Tag not found",
                    "message": f"Tag {tag_id} not found or access denied"
                }

            return {
                "success": True,
                "message": f"Tag {tag_id} deleted successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete tag: {str(e)}"
            }
        finally:
            break


@server.tool()
async def get_stats(user_id: str) -> dict:
    """
    Get dashboard statistics and task summary.

    Shows:
    - Total tasks, completed, in-progress, overdue
    - Completion rate
    - Priority distribution
    - Weekly stats

    Args:
        user_id: User ID from authentication

    Returns:
        Comprehensive task statistics

    Examples:
        - "Show my stats"
        - "What's my task summary?"
        - "How many tasks do I have?"
    """
    async for session in get_session():
        try:
            from src.services.stats_service import StatsService

            stats = await StatsService.get_task_summary(
                user_id=user_id,
                session=session
            )

            return {
                "success": True,
                "stats": stats,
                "message": f"You have {stats['total_tasks']} total tasks, {stats['completed_tasks']} completed"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get stats: {str(e)}"
            }
        finally:
            break


@server.tool()
async def add_comment(
    user_id: str,
    task_id: int,
    content: str,
    mentions: Optional[List[str]] = None
) -> dict:
    """
    Add a comment to a task.

    Args:
        user_id: User ID from authentication
        task_id: Task ID to comment on
        content: Comment text
        mentions: Optional list of user IDs to mention

    Returns:
        Success status and created comment

    Examples:
        - "Add comment to task 5: 'Working on this now'"
        - "Comment on meeting task: 'Postponed to next week'"
    """
    async for session in get_session():
        try:
            from src.services.comment_service import CommentService
            from src.models.comment import CommentCreate

            comment_data = CommentCreate(
                content=content,
                mentions=mentions or []
            )

            result = await CommentService.create_comment(
                task_id=task_id,
                user_id=user_id,
                comment_data=comment_data,
                session=session
            )

            if not result:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"Task {task_id} not found"
                }

            return {
                "success": True,
                "comment": {
                    "id": result.id,
                    "content": result.content,
                    "created_at": str(result.created_at)
                },
                "message": "Comment added successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to add comment: {str(e)}"
            }
        finally:
            break


@server.tool()
async def get_comments(
    user_id: str,
    task_id: int
) -> dict:
    """
    Get all comments for a task.

    Args:
        user_id: User ID from authentication
        task_id: Task ID

    Returns:
        List of comments

    Examples:
        - "Show comments for task 5"
        - "What are the comments on meeting task?"
    """
    async for session in get_session():
        try:
            from src.services.comment_service import CommentService

            comments = await CommentService.get_task_comments(
                task_id=task_id,
                session=session
            )

            return {
                "success": True,
                "comments": [
                    {
                        "id": c.id,
                        "content": c.content,
                        "author_id": c.author_id,
                        "created_at": str(c.created_at)
                    }
                    for c in comments
                ],
                "count": len(comments),
                "message": f"Found {len(comments)} comment(s)"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get comments: {str(e)}"
            }
        finally:
            break


@server.tool()
async def delete_comment(
    user_id: str,
    comment_id: int
) -> dict:
    """
    Delete a comment.

    Only the comment author can delete it.

    Args:
        user_id: User ID from authentication
        comment_id: Comment ID to delete

    Returns:
        Success status

    Examples:
        - "Delete comment 10"
        - "Remove my last comment"
    """
    async for session in get_session():
        try:
            from src.services.comment_service import CommentService

            result = await CommentService.delete_comment(
                comment_id=comment_id,
                user_id=user_id,
                session=session
            )

            if not result:
                return {
                    "success": False,
                    "error": "Comment not found or unauthorized",
                    "message": f"Comment {comment_id} not found or you don't have permission"
                }

            return {
                "success": True,
                "message": f"Comment {comment_id} deleted successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete comment: {str(e)}"
            }
        finally:
            break


# Run MCP server
if __name__ == "__main__":
    print("Starting TaskNest MCP Server...")
    print("Tools available:")
    print("  - create_task")
    print("  - list_tasks")
    print("  - complete_task")
    print("  - update_task")
    print("  - delete_task")
    print("  - list_tags")
    print("  - create_tag")
    print("  - delete_tag")
    print("  - get_stats")
    print("  - add_comment")
    print("  - get_comments")
    print("  - delete_comment")
    print("\nServer running on port 8002...")

    asyncio.run(server.run(port=8002))
