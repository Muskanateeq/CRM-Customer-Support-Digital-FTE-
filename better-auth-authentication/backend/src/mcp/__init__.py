"""
MCP Tools Module

Model Context Protocol tools for task management.
These tools are exposed to the LLM for function calling.
"""

from src.mcp.tools import (
    create_task_tool,
    list_tasks_tool,
    update_task_tool,
    complete_task_tool,
    delete_task_tool,
    get_all_tools,
    execute_tool
)

__all__ = [
    "create_task_tool",
    "list_tasks_tool",
    "update_task_tool",
    "complete_task_tool",
    "delete_task_tool",
    "get_all_tools",
    "execute_tool",
]
