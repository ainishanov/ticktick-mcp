"""TickTick MCP Server - Main server implementation."""

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import AnyUrl

from .api import TickTickAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ticktick-mcp")

# Initialize server
server = Server("ticktick-mcp")

# API client (initialized lazily)
_api: TickTickAPI | None = None


def get_api() -> TickTickAPI:
    """Get or create TickTick API client."""
    global _api
    if _api is None:
        _api = TickTickAPI()
    return _api


def format_task(task: dict) -> str:
    """Format a task for display."""
    priority_map = {0: "⚪", 1: "🔵", 3: "🟡", 5: "🔴"}
    priority = priority_map.get(task.get("priority", 0), "⚪")

    title = task.get("title", "Untitled")
    project = task.get("_project_name", "")
    due = task.get("dueDate", "")[:10] if task.get("dueDate") else ""

    parts = [f"{priority} {title}"]
    if project:
        parts.append(f"[{project}]")
    if due:
        parts.append(f"📅 {due}")

    return " ".join(parts)


def format_tasks_list(tasks: list[dict]) -> str:
    """Format a list of tasks for display."""
    if not tasks:
        return "No tasks found."

    lines = [f"Found {len(tasks)} task(s):\n"]
    for task in tasks:
        lines.append(f"  • {format_task(task)}")
        lines.append(f"    ID: {task.get('id', 'N/A')} | Project ID: {task.get('projectId', 'N/A')}")

    return "\n".join(lines)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_projects",
            description="Get all projects (lists) from TickTick",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_tasks",
            description="Get tasks from TickTick. Can filter by project or get all tasks.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID to filter tasks. If not provided, returns tasks from all projects.",
                    },
                },
            },
        ),
        Tool(
            name="get_today_tasks",
            description="Get all tasks due today",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_high_priority_tasks",
            description="Get tasks with high priority (🔴) or medium priority (🟡)",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_priority": {
                        "type": "integer",
                        "enum": [1, 3, 5],
                        "description": "Minimum priority level: 1=Low, 3=Medium, 5=High. Default is 3 (Medium+High).",
                    },
                },
            },
        ),
        Tool(
            name="create_task",
            description="Create a new task in TickTick",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title (required)",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project ID. If not provided, task goes to Inbox.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Task description/notes",
                    },
                    "priority": {
                        "type": "integer",
                        "enum": [0, 1, 3, 5],
                        "description": "Priority: 0=None, 1=Low, 3=Medium, 5=High",
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in YYYY-MM-DD format",
                    },
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="complete_task",
            description="Mark a task as complete",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project ID where the task belongs",
                    },
                },
                "required": ["task_id", "project_id"],
            },
        ),
        Tool(
            name="update_task",
            description="Update an existing task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project ID where the task belongs",
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title",
                    },
                    "content": {
                        "type": "string",
                        "description": "New task description",
                    },
                    "priority": {
                        "type": "integer",
                        "enum": [0, 1, 3, 5],
                        "description": "New priority: 0=None, 1=Low, 3=Medium, 5=High",
                    },
                    "due_date": {
                        "type": "string",
                        "description": "New due date in YYYY-MM-DD format",
                    },
                },
                "required": ["task_id", "project_id"],
            },
        ),
        Tool(
            name="delete_task",
            description="Delete a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project ID where the task belongs",
                    },
                },
                "required": ["task_id", "project_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    api = get_api()

    try:
        if name == "get_projects":
            projects = await api.get_projects()
            if not projects:
                return [TextContent(type="text", text="No projects found.")]

            lines = [f"Found {len(projects)} project(s):\n"]
            for p in projects:
                lines.append(f"  • {p.get('name', 'Untitled')}")
                lines.append(f"    ID: {p.get('id', 'N/A')}")

            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "get_tasks":
            project_id = arguments.get("project_id")
            tasks = await api.get_all_tasks(project_id)
            return [TextContent(type="text", text=format_tasks_list(tasks))]

        elif name == "get_today_tasks":
            tasks = await api.get_today_tasks()
            result = format_tasks_list(tasks)
            if tasks:
                result = f"📅 Tasks due TODAY:\n\n{result}"
            else:
                result = "✅ No tasks due today!"
            return [TextContent(type="text", text=result)]

        elif name == "get_high_priority_tasks":
            min_priority = arguments.get("min_priority", 3)
            tasks = await api.get_tasks_by_priority(min_priority)
            priority_label = {1: "Low+", 3: "Medium+", 5: "High"}.get(min_priority, "")
            result = format_tasks_list(tasks)
            if tasks:
                result = f"🎯 {priority_label} priority tasks:\n\n{result}"
            return [TextContent(type="text", text=result)]

        elif name == "create_task":
            task = await api.create_task(
                title=arguments["title"],
                project_id=arguments.get("project_id"),
                content=arguments.get("content"),
                priority=arguments.get("priority", 0),
                due_date=arguments.get("due_date"),
            )
            return [TextContent(
                type="text",
                text=f"✅ Task created: {task.get('title', 'Untitled')}\nID: {task.get('id', 'N/A')}",
            )]

        elif name == "complete_task":
            await api.complete_task(
                task_id=arguments["task_id"],
                project_id=arguments["project_id"],
            )
            return [TextContent(type="text", text="✅ Task marked as complete!")]

        elif name == "update_task":
            task = await api.update_task(
                task_id=arguments["task_id"],
                project_id=arguments["project_id"],
                title=arguments.get("title"),
                content=arguments.get("content"),
                priority=arguments.get("priority"),
                due_date=arguments.get("due_date"),
            )
            return [TextContent(type="text", text=f"✅ Task updated: {task.get('title', 'Untitled')}")]

        elif name == "delete_task":
            await api.delete_task(
                task_id=arguments["task_id"],
                project_id=arguments["project_id"],
            )
            return [TextContent(type="text", text="🗑️ Task deleted.")]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Error in {name}: {e}")
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
