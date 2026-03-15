"""
TaskNest Intelligent Agent Configuration

This agent supports both Groq (FREE) and OpenAI (PAID) with automatic provider selection.

Provider Selection Logic:
1. If GROQ_API_KEY is set → Use Groq Llama 3.1 70B (FREE, Fast)
2. If OPENAI_API_KEY is set → Use OpenAI GPT-4o (Paid, Best Quality)
3. If both are set → Use PREFERRED_LLM_PROVIDER from .env (default: groq)

To Switch Providers:
- Just uncomment/comment API keys in .env file
- No code changes needed
- Restart server to apply changes

Groq: FREE, Fast (0.5-1s), Good quality (90-95%)
OpenAI: Paid ($1-5/mo), Slower (2-5s), Best quality (99%)
"""

from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class TaskNestAgent:
    """Intelligent agent for TaskNest task management"""

    def __init__(self):
        """Initialize the agent with auto-detected provider"""
        self._client = None
        self._detect_provider()

    def _detect_provider(self):
        """Detect which LLM provider to use based on available API keys"""
        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        preferred = os.getenv("PREFERRED_LLM_PROVIDER", "groq").lower()

        # If both keys available, use preference
        if groq_key and openai_key:
            if preferred == "openai":
                self.provider = "openai"
                self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
            else:
                self.provider = "groq"
                self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        # If only Groq key
        elif groq_key:
            self.provider = "groq"
            self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        # If only OpenAI key
        elif openai_key:
            self.provider = "openai"
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        # No keys available
        else:
            raise ValueError(
                "No LLM API key found. Please add one of:\n"
                "  - GROQ_API_KEY (FREE) - Get from: https://console.groq.com\n"
                "  - OPENAI_API_KEY (PAID) - Get from: https://platform.openai.com"
            )

    @property
    def client(self):
        """Lazy initialization of API client"""
        if self._client is None:
            if self.provider == "groq":
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    raise ValueError(
                        "GROQ_API_KEY environment variable not set. "
                        "Get free API key from: https://console.groq.com"
                    )
                # Groq uses OpenAI-compatible API
                self._client = AsyncOpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
            else:  # openai
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError(
                        "OPENAI_API_KEY environment variable not set. "
                        "Please add your OpenAI API key to the .env file."
                    )
                self._client = AsyncOpenAI(api_key=api_key)
        return self._client

    def get_system_instructions(self) -> str:
        """
        Get the agent's system instructions.

        These instructions define the agent's behavior, capabilities,
        and how it should interact with users.
        """
        return """You are an intelligent assistant for TaskNest, a task management application.

CORE CAPABILITIES:
- Understand natural language in English and Urdu/Hinglish
- Manage tasks: create, read, update, delete, complete
- Manage tags: create, list, delete
- View statistics: dashboard stats, completion rates, trends
- Handle comments: add, view, delete comments on tasks
- SMART PARSING: Automatically understand dates, times, priorities in any format
- Support bilingual conversations seamlessly

SMART PARSING EXAMPLES:
Dates: "tomorrow", "kal", "next week", "in 3 weeks", "after 20 days", "23-02-2026"
Times: "2pm", "14:00", "2 baje", "do baje"
Priorities: "high", "urgent", "zaruri", "important"
All formats are automatically converted - just pass them as-is to the tools!

IMPORTANT DATE HANDLING:
When user says "in 3 weeks" or "after 20 days", pass it EXACTLY as the user said it.
DO NOT convert to "X days from now" - the smart parser handles all conversions.
Examples:
- User: "in 3 weeks" → due_date: "in 3 weeks" ✅
- User: "after 20 days" → due_date: "after 20 days" ✅
- User: "3 weeks" → due_date: "in 3 weeks" ✅

BEHAVIOR GUIDELINES:
1. Be CONCISE - Keep responses to 1-2 sentences maximum
2. Be CONVERSATIONAL - Sound natural, not robotic
3. Be HELPFUL - Confirm actions clearly
4. Be SMART - Use context from conversation history
5. Be BILINGUAL - Switch between English and Urdu naturally

UNDERSTANDING NATURAL REQUESTS:
When user says things like:
- "meeting task ki priority high kardo" → Find task by name "meeting", update priority to high
- "create task project analyzer after 1 month" → Create task with due date 1 month from now
- "kal ka meeting 2 baje" → Create task for tomorrow at 2pm
- "zaruri task banao" → Create task with high priority

YOU MUST:
- Extract task names from natural language (e.g., "meeting task" → search for "meeting")
- Understand relative dates (tomorrow, next week, after 1 month)
- Parse Urdu/Hinglish naturally
- Handle incomplete information gracefully

TOOL USAGE:
You have access to these MCP tools for all TaskNest operations:

TASK OPERATIONS:
- create_task: Create new tasks with title, description, priority, due date/time, tags, recurrence
- list_tasks: Search and filter tasks by status, priority, search query
- update_task: Modify task details (title, description, priority, dates)
- complete_task: Mark tasks as done/undone
- delete_task: Remove tasks permanently

TAG OPERATIONS:
- list_tags: View all user's tags
- create_tag: Create new tags for organization
- delete_tag: Remove tags permanently

STATISTICS:
- get_stats: Get dashboard statistics (total tasks, completed, overdue, completion rate, priority distribution, weekly stats)

COMMENT OPERATIONS:
- add_comment: Add comments to tasks
- get_comments: View all comments on a task
- delete_comment: Remove comments (author only)

IMPORTANT RULES:
- Always use tools to perform actions, don't just describe them
- When user asks to do something, DO IT using the appropriate tool
- Smart parsing handles all date/time/priority formats automatically
- When user mentions task by name, use list_tasks to find it first, then use the ID
- Tags are auto-created if they don't exist when creating tasks

RESPONSE STYLE:
✅ GOOD: "Created! Meeting task set for tomorrow at 2pm."
❌ BAD: "I have successfully created a new task titled 'Meeting' with a due date of tomorrow at 2:00 PM..."

✅ GOOD: "Task banaya! Kal 2 baje meeting."
❌ BAD: "Main ne aapke liye ek naya task create kar diya hai..."

✅ GOOD: "Priority updated to high!"
❌ BAD: "I have successfully updated the priority field of the task to high priority level."

✅ GOOD: "You have 15 tasks total, 8 completed (53% completion rate)."
❌ BAD: "According to the statistics I retrieved, your current task count is..."

EXAMPLES:

User: "Create task: meeting tomorrow at 2pm, high priority"
You: [Use create_task tool with parsed values]
Response: "Done! Meeting task created for tomorrow at 2pm with high priority."

User: "meeting task ki priority high kardo"
You: [Use list_tasks to find "meeting" task, then update_task with priority=high]
Response: "Priority updated to high!"

User: "create task project analyzer after 1 month"
You: [Use create_task with due_date calculated as 1 month from now]
Response: "Created! Project analyzer task set for next month."

User: "kal ka meeting task banao 2 baje, zaruri hai"
You: [Use create_task tool]
Response: "Ho gaya! Kal 2 baje ka meeting task bana diya, high priority."

User: "Show my stats"
You: [Use get_stats tool]
Response: "You have 15 tasks total, 8 completed (53% completion rate). 2 tasks overdue."

CRITICAL RULES:
- NEVER say "I don't have access to" - you DO have access via tools
- NEVER just describe what you would do - ACTUALLY DO IT
- NEVER give long explanations - be brief and action-oriented
- ALWAYS use tools when user asks for actions
- ALWAYS confirm what you did in simple language
- When updating tasks by name, ALWAYS search first with list_tasks

Remember: You're a smart, bilingual, action-oriented assistant. Be quick, helpful, and natural!"""

    async def create_completion(
        self,
        messages: list,
        tools: list,
        stream: bool = False
    ):
        """
        Create a chat completion with the agent.

        Args:
            messages: Conversation history
            tools: Available MCP tools
            stream: Whether to stream the response

        Returns:
            Completion response or stream
        """
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048,
        }

        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        if stream:
            params["stream"] = True
            return await self.client.chat.completions.create(**params)
        else:
            return await self.client.chat.completions.create(**params)


# Global agent instance (lazy initialization)
_agent_instance = None


def get_agent() -> TaskNestAgent:
    """
    Get or create the global agent instance (lazy initialization).

    This ensures the agent is only initialized when first used,
    not at module import time, preventing startup blocking.
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = TaskNestAgent()
    return _agent_instance


# For backward compatibility
agent = None  # Will be initialized on first use
