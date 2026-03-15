"""
MCP Tools for Task Management

These tools wrap the existing TaskService methods and expose them
to the LLM for function calling via the Model Context Protocol.
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.task_service import TaskService
from src.models.task import TaskCreate, TaskUpdate, TaskCompletionToggle


# Tool 1: Create Task
create_task_tool = {
    "type": "function",
    "function": {
        "name": "create_task",
        "description": "Create a new task for the user. Use this when the user wants to add a task, todo, or reminder.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The task title or description"
                },
                "description": {
                    "type": "string",
                    "description": "Optional detailed description of the task"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Task priority level (default: medium)"
                },
                "due_date": {
                    "type": "string",
                    "description": (
                        "Optional due date. Accepts multiple formats:\n"
                        "- Natural language: 'tomorrow', 'next week', 'after 3 weeks', 'in 2 months'\n"
                        "- Urdu: 'kal', 'parso', 'aaj'\n"
                        "- Standard format: 'YYYY-MM-DD' (e.g., '2026-03-15')\n"
                        "- DD-MM-YYYY: '15-03-2026'\n"
                        "Smart parser will automatically convert to correct format."
                    )
                },
                "due_time": {
                    "type": "string",
                    "description": "Optional due time in HH:MM format (24-hour)"
                },
                "recurrence_pattern": {
                    "type": "string",
                    "enum": ["daily", "weekly", "monthly"],
                    "description": "Optional recurrence pattern for recurring tasks"
                },
                "tag_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of tag names (e.g., ['work', 'urgent']). Tags will be created if they don't exist."
                },
                "tag_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Optional list of tag IDs (use tag_names instead for easier usage)"
                }
            },
            "required": ["title"]
        }
    }
}


# Tool 2: List Tasks
list_tasks_tool = {
    "type": "function",
    "function": {
        "name": "list_tasks",
        "description": "Get a list of the user's tasks. Use this when the user wants to see their tasks, todos, or check what they need to do.",
        "parameters": {
            "type": "object",
            "properties": {
                "search": {
                    "type": "string",
                    "description": "Optional search query to filter tasks by title or description"
                },
                "status": {
                    "type": "string",
                    "enum": ["all", "active", "completed"],
                    "description": "Filter by completion status (default: all)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Filter by priority level"
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["created_at", "due_date", "priority", "title"],
                    "description": "Sort field (default: created_at)"
                },
                "sort_order": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "Sort order (default: desc)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of tasks to return (default: 50)"
                }
            },
            "required": []
        }
    }
}


# Tool 3: Update Task
update_task_tool = {
    "type": "function",
    "function": {
        "name": "update_task",
        "description": (
            "Update an existing task's details. "
            "IMPORTANT: task_id must be a NUMERIC ID (e.g., '5', '123'). "
            "If user refers to task by name/title, you MUST first call list_tasks with search parameter to find the numeric ID. "
            "Example workflow: User says 'update hackathon task' → call list_tasks(search='hackathon') → get task_id → call update_task(task_id='5', ...)"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The NUMERIC ID of the task to update (e.g., '1', '5', '123'). Get this from list_tasks if user refers to task by name."
                },
                "title": {
                    "type": "string",
                    "description": "New task title"
                },
                "description": {
                    "type": "string",
                    "description": "New task description"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "New priority level"
                },
                "due_date": {
                    "type": "string",
                    "description": "New due date in YYYY-MM-DD format"
                },
                "due_time": {
                    "type": "string",
                    "description": "New due time in HH:MM format (24-hour)"
                },
                "recurrence_pattern": {
                    "type": "string",
                    "enum": ["daily", "weekly", "monthly"],
                    "description": "New recurrence pattern"
                }
            },
            "required": ["task_id"]
        }
    }
}


# Tool 4: Complete Task
complete_task_tool = {
    "type": "function",
    "function": {
        "name": "complete_task",
        "description": (
            "Mark a task as completed or uncompleted. "
            "IMPORTANT: task_id must be a NUMERIC ID (e.g., '5', '123'). "
            "If user refers to task by name/title (e.g., 'complete the hackathon task'), you MUST first call list_tasks with search parameter to find the numeric ID. "
            "Example workflow: User says 'mark hackathon task as done' → call list_tasks(search='hackathon') → get task_id='5' → call complete_task(task_id='5', completed=true)"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The NUMERIC ID of the task (e.g., '1', '5', '123'). Get this from list_tasks if user refers to task by name."
                },
                "completed": {
                    "type": "boolean",
                    "description": "True to mark as completed, False to mark as incomplete"
                }
            },
            "required": ["task_id", "completed"]
        }
    }
}


# Tool 5: Delete Task
delete_task_tool = {
    "type": "function",
    "function": {
        "name": "delete_task",
        "description": (
            "Delete a task permanently. "
            "IMPORTANT: task_id must be a NUMERIC ID (e.g., '5', '123'). "
            "If user refers to task by name/title, you MUST first call list_tasks with search parameter to find the numeric ID. "
            "Example workflow: User says 'delete the meeting task' → call list_tasks(search='meeting') → get task_id='10' → call delete_task(task_id='10')"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The NUMERIC ID of the task to delete (e.g., '1', '5', '123'). Get this from list_tasks if user refers to task by name."
                }
            },
            "required": ["task_id"]
        }
    }
}


# Tool 6: Create Tag
create_tag_tool = {
    "type": "function",
    "function": {
        "name": "create_tag",
        "description": "Create a new tag for organizing tasks.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Tag name (e.g., 'work', 'urgent', 'personal')"
                }
            },
            "required": ["name"]
        }
    }
}


# Tool 7: Delete Tag
delete_tag_tool = {
    "type": "function",
    "function": {
        "name": "delete_tag",
        "description": "Delete a tag permanently.",
        "parameters": {
            "type": "object",
            "properties": {
                "tag_id": {
                    "type": "integer",
                    "description": "Tag ID to delete"
                }
            },
            "required": ["tag_id"]
        }
    }
}


# Tool 8: Get Stats
get_stats_tool = {
    "type": "function",
    "function": {
        "name": "get_stats",
        "description": (
            "Get dashboard statistics and task summary. "
            "Shows total tasks, completed, in-progress, overdue, completion rate, "
            "priority distribution, and weekly stats."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


# Tool 9: Add Comment
add_comment_tool = {
    "type": "function",
    "function": {
        "name": "add_comment",
        "description": "Add a comment to a task.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "Task ID to comment on"
                },
                "content": {
                    "type": "string",
                    "description": "Comment text"
                }
            },
            "required": ["task_id", "content"]
        }
    }
}


# Tool 10: Get Comments
get_comments_tool = {
    "type": "function",
    "function": {
        "name": "get_comments",
        "description": "Get all comments for a task.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "Task ID"
                }
            },
            "required": ["task_id"]
        }
    }
}


# Tool 11: Delete Comment
delete_comment_tool = {
    "type": "function",
    "function": {
        "name": "delete_comment",
        "description": "Delete a comment. Only the comment author can delete it.",
        "parameters": {
            "type": "object",
            "properties": {
                "comment_id": {
                    "type": "integer",
                    "description": "Comment ID to delete"
                }
            },
            "required": ["comment_id"]
        }
    }
}


# Tool 12: List Tags
list_tags_tool = {
    "type": "function",
    "function": {
        "name": "list_tags",
        "description": "List all user's tags.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


def get_all_tools() -> List[Dict[str, Any]]:
    """
    Get all available MCP tools.

    Returns:
        List of tool definitions in OpenAI function calling format
    """
    return [
        create_task_tool,
        list_tasks_tool,
        update_task_tool,
        complete_task_tool,
        delete_task_tool,
        list_tags_tool,
        create_tag_tool,
        delete_tag_tool,
        get_stats_tool,
        add_comment_tool,
        get_comments_tool,
        delete_comment_tool,
    ]


async def execute_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    user_id: str,
    session: AsyncSession
) -> Dict[str, Any]:
    """
    Execute a tool by name with the given arguments.

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments as a dictionary (can be None or empty)
        user_id: User ID from JWT token
        session: Database session

    Returns:
        Tool execution result

    Raises:
        ValueError: If tool name is invalid
    """
    # Ensure arguments is a dict (handle None case)
    if arguments is None:
        arguments = {}

    # Helper function to resolve task_id (numeric or name-based search)
    async def resolve_task_id(args: Dict[str, Any]) -> int:
        """
        Convert task_id to integer, with automatic name resolution.

        If task_id is not numeric, searches for tasks by name and returns the first match.
        This handles cases where LLM passes task names instead of IDs.

        Improvements:
        - Fuzzy matching (removes common filler words)
        - Better error messages with suggestions
        """
        task_id = args.get("task_id")
        if task_id is None:
            raise ValueError("task_id is required")

        # Try direct integer conversion first
        try:
            return int(task_id)
        except (ValueError, TypeError):
            # task_id is not numeric - treat it as a task name/search query
            pass

        # Clean search query - remove common filler words
        search_query = str(task_id).strip().lower()

        # Remove common words that don't help search (English + Urdu/Hindi)
        filler_words = [
            "task", "the", "a", "an", "my", "to", "ko", "kardo", "mark", "as",
            "complete", "completed", "done", "finish", "finished",
            "delete", "remove", "update", "change", "modify",
            "karo", "kar", "do", "dedo", "karna", "hai", "tha", "ho",
            "please", "can", "you", "i", "want", "need"
        ]
        for word in filler_words:
            search_query = search_query.replace(f" {word} ", " ")
            search_query = search_query.replace(f"{word} ", "")
            search_query = search_query.replace(f" {word}", "")

        search_query = search_query.strip()

        if not search_query:
            raise ValueError("task_id cannot be empty after cleaning")

        # Call list_tasks to find matching task
        tasks = await TaskService.get_user_tasks(
            user_id=user_id,
            session=session,
            search=search_query,
            status="all",
            limit=10
        )

        if not tasks:
            # Provide helpful error with available tasks
            all_tasks = await TaskService.get_user_tasks(
                user_id=user_id,
                session=session,
                status="all",
                limit=5
            )

            if all_tasks:
                task_list = ", ".join([f"'{t.title}' (ID: {t.id})" for t in all_tasks[:3]])
                raise ValueError(
                    f"No task found matching '{search_query}'. "
                    f"Available tasks: {task_list}. "
                    f"Try using the task ID number or create the task first."
                )
            else:
                raise ValueError(
                    f"No task found matching '{search_query}'. "
                    f"You don't have any tasks yet. Create one first with: 'Create a task called {search_query}'"
                )

        # Return the first matching task's ID
        resolved_id = tasks[0].id
        return resolved_id

    if tool_name == "create_task":
        # SMART PARSING: Parse dates, times, priorities intelligently
        from src.utils.smart_parser import SmartParser

        # Parse due_date if provided
        due_date = arguments.get("due_date")
        if due_date:
            parsed_date = SmartParser.parse_date(due_date)
            if parsed_date:
                due_date = parsed_date

        # Parse due_time if provided
        due_time = arguments.get("due_time")
        if due_time:
            parsed_time = SmartParser.parse_time(due_time)
            if parsed_time:
                due_time = parsed_time

        # Parse priority if provided
        priority = arguments.get("priority", "medium")
        if priority:
            priority = SmartParser.parse_priority(priority)

        # Handle tag names - convert to tag IDs or create new tags
        tag_ids = arguments.get("tag_ids", [])
        tag_names = arguments.get("tag_names", [])

        # If tag_names provided, resolve to IDs (create if needed)
        if tag_names:
            from src.services.tag_service import TagService
            from src.models.tag import TagCreate

            resolved_tag_ids = []
            for tag_name in tag_names:
                tag_name_clean = tag_name.strip().lower()

                # Get all user tags and search manually
                all_tags = await TagService.get_user_tags(
                    user_id=user_id,
                    session=session
                )

                # Find matching tag (case-insensitive)
                matching_tag = None
                for tag in all_tags:
                    if tag.name.lower() == tag_name_clean:
                        matching_tag = tag
                        break

                if matching_tag:
                    # Use existing tag
                    resolved_tag_ids.append(matching_tag.id)
                else:
                    # Create new tag with original casing
                    new_tag = await TagService.create_tag(
                        user_id=user_id,
                        tag_data=TagCreate(name=tag_name.strip()),
                        session=session
                    )
                    resolved_tag_ids.append(new_tag.id)

            tag_ids.extend(resolved_tag_ids)

        # Create TaskCreate model from arguments (with parsed values)
        task_data = TaskCreate(
            title=arguments["title"],
            description=arguments.get("description"),
            priority=priority,
            due_date=due_date,
            due_time=due_time,
            recurrence_pattern=arguments.get("recurrence_pattern"),
            tag_ids=tag_ids
        )
        result = await TaskService.create_task(user_id, task_data, session)

        # Activity is already logged in TaskService.create_task

        return {
            "success": True,
            "task": result.model_dump(mode='json'),
            "message": f"Task '{result.title}' created successfully"
        }

    elif tool_name == "list_tasks":
        # Get tasks with filters
        tasks = await TaskService.get_user_tasks(
            user_id=user_id,
            session=session,
            search=arguments.get("search"),
            status=arguments.get("status", "all"),
            priority=arguments.get("priority"),
            sort_by=arguments.get("sort_by", "created_at"),
            sort_order=arguments.get("sort_order", "desc"),
            limit=arguments.get("limit", 50)
        )
        return {
            "success": True,
            "tasks": [task.model_dump(mode='json') for task in tasks],
            "count": len(tasks),
            "message": f"Found {len(tasks)} task(s)"
        }

    elif tool_name == "update_task":
        # SMART PARSING: Parse dates, times, priorities intelligently
        from src.utils.smart_parser import SmartParser

        # Resolve task_id (numeric or name-based search)
        task_id = await resolve_task_id(arguments)

        # Parse due_date if provided
        due_date = arguments.get("due_date")
        if due_date:
            parsed_date = SmartParser.parse_date(due_date)
            if parsed_date:
                due_date = parsed_date

        # Parse due_time if provided
        due_time = arguments.get("due_time")
        if due_time:
            parsed_time = SmartParser.parse_time(due_time)
            if parsed_time:
                due_time = parsed_time

        # Parse priority if provided
        priority = arguments.get("priority")
        if priority:
            priority = SmartParser.parse_priority(priority)

        # Remove task_id from arguments before creating TaskUpdate
        update_args = {
            "title": arguments.get("title"),
            "description": arguments.get("description"),
            "priority": priority,
            "due_date": due_date,
            "due_time": due_time,
            "recurrence_pattern": arguments.get("recurrence_pattern")
        }
        # Remove None values
        update_args = {k: v for k, v in update_args.items() if v is not None}

        task_data = TaskUpdate(**update_args)
        result = await TaskService.update_task(task_id, user_id, task_data, session)

        # Handle None case (task not found)
        if not result:
            return {
                "success": False,
                "error": "Task not found",
                "message": f"Task {task_id} not found or access denied"
            }

        return {
            "success": True,
            "task": result.model_dump(mode='json'),
            "message": f"Task '{result.title}' updated successfully"
        }

    elif tool_name == "complete_task":
        # Resolve task_id (numeric or name-based search)
        task_id = await resolve_task_id(arguments)
        completed = arguments["completed"]
        result = await TaskService.toggle_completion(task_id, user_id, completed, session)
        status = "completed" if completed else "incomplete"
        return {
            "success": True,
            "task": result.model_dump(mode='json'),
            "message": f"Task '{result.title}' marked as {status}"
        }

    elif tool_name == "delete_task":
        # Resolve task_id (numeric or name-based search)
        task_id = await resolve_task_id(arguments)
        await TaskService.delete_task(task_id, user_id, session)
        return {
            "success": True,
            "message": f"Task deleted successfully"
        }

    elif tool_name == "list_tags":
        # Get all user tags
        from src.services.tag_service import TagService
        tags = await TagService.get_user_tags(user_id=user_id, session=session)
        return {
            "success": True,
            "tags": [{"id": t.id, "name": t.name} for t in tags],
            "count": len(tags),
            "message": f"Found {len(tags)} tag(s)"
        }

    elif tool_name == "create_tag":
        # Create new tag
        from src.services.tag_service import TagService
        from src.models.tag import TagCreate

        tag_data = TagCreate(name=arguments["name"])
        result = await TagService.create_tag(
            user_id=user_id,
            tag_data=tag_data,
            session=session
        )

        if not result:
            return {
                "success": False,
                "error": "Tag already exists",
                "message": f"Tag '{arguments['name']}' already exists"
            }

        return {
            "success": True,
            "tag": {"id": result.id, "name": result.name},
            "message": f"Tag '{result.name}' created successfully"
        }

    elif tool_name == "delete_tag":
        # Delete tag
        from src.services.tag_service import TagService

        result = await TagService.delete_tag(
            tag_id=arguments["tag_id"],
            user_id=user_id,
            session=session
        )

        if not result:
            return {
                "success": False,
                "error": "Tag not found",
                "message": f"Tag {arguments['tag_id']} not found or access denied"
            }

        return {
            "success": True,
            "message": f"Tag deleted successfully"
        }

    elif tool_name == "get_stats":
        # Get dashboard statistics
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

    elif tool_name == "add_comment":
        # Add comment to task
        from src.services.comment_service import CommentService
        from src.models.comment import CommentCreate

        comment_data = CommentCreate(
            content=arguments["content"],
            mentions=arguments.get("mentions", [])
        )

        result = await CommentService.create_comment(
            task_id=arguments["task_id"],
            user_id=user_id,
            comment_data=comment_data,
            session=session
        )

        if not result:
            return {
                "success": False,
                "error": "Task not found",
                "message": f"Task {arguments['task_id']} not found"
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

    elif tool_name == "get_comments":
        # Get all comments for a task
        from src.services.comment_service import CommentService

        comments = await CommentService.get_task_comments(
            task_id=arguments["task_id"],
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

    elif tool_name == "delete_comment":
        # Delete comment
        from src.services.comment_service import CommentService

        result = await CommentService.delete_comment(
            comment_id=arguments["comment_id"],
            user_id=user_id,
            session=session
        )

        if not result:
            return {
                "success": False,
                "error": "Comment not found or unauthorized",
                "message": f"Comment {arguments['comment_id']} not found or you don't have permission"
            }

        return {
            "success": True,
            "message": "Comment deleted successfully"
        }

    else:
        raise ValueError(f"Unknown tool: {tool_name}")
