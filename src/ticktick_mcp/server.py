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
    tags = task.get("tags", [])

    parts = [f"{priority} {title}"]
    if project:
        parts.append(f"[{project}]")
    if due:
        parts.append(f"📅 {due}")
    if tags:
        parts.append(f"🏷️ {', '.join(tags)}")

    return " ".join(parts)


def format_tasks_list(tasks: list[dict], show_subtasks: bool = False) -> str:
    """Format a list of tasks for display."""
    if not tasks:
        return "No tasks found."

    lines = [f"Found {len(tasks)} task(s):\n"]
    for task in tasks:
        lines.append(f"  • {format_task(task)}")
        lines.append(f"    ID: {task.get('id', 'N/A')} | Project ID: {task.get('projectId', 'N/A')}")

        # Show subtasks if requested
        if show_subtasks:
            items = task.get("items", [])
            if items:
                for item in items:
                    status = "✓" if item.get("status") == 1 else "○"
                    lines.append(f"      {status} {item.get('title', '')}")

    return "\n".join(lines)


def format_project(project: dict) -> str:
    """Format a project for display."""
    name = project.get("name", "Untitled")
    color = project.get("color", "")
    view_mode = project.get("viewMode", "list")
    return f"📁 {name} ({view_mode}) {color}"


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        # ==================== PROJECT TOOLS ====================
        Tool(
            name="get_projects",
            description="Get all projects (lists) from TickTick",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_project_by_id",
            description="Get a specific project by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID",
                    },
                },
                "required": ["project_id"],
            },
        ),
        Tool(
            name="get_project_with_data",
            description="Get project details along with all tasks and columns (for kanban)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID",
                    },
                },
                "required": ["project_id"],
            },
        ),
        Tool(
            name="create_project",
            description="Create a new project in TickTick",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Project name (required)",
                    },
                    "color": {
                        "type": "string",
                        "description": "Project color in hex format (e.g., '#4772FA')",
                    },
                    "view_mode": {
                        "type": "string",
                        "enum": ["list", "kanban", "timeline"],
                        "description": "View mode: list, kanban, or timeline",
                    },
                    "kind": {
                        "type": "string",
                        "enum": ["TASK", "NOTE"],
                        "description": "Project kind: TASK or NOTE",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="update_project",
            description="Update an existing project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID (required)",
                    },
                    "name": {
                        "type": "string",
                        "description": "New project name",
                    },
                    "color": {
                        "type": "string",
                        "description": "New color in hex format",
                    },
                    "view_mode": {
                        "type": "string",
                        "enum": ["list", "kanban", "timeline"],
                        "description": "New view mode",
                    },
                },
                "required": ["project_id"],
            },
        ),
        Tool(
            name="delete_project",
            description="Delete a project (WARNING: deletes all tasks in it!)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID to delete",
                    },
                },
                "required": ["project_id"],
            },
        ),
        # ==================== TASK QUERY TOOLS ====================
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
            name="get_overdue_tasks",
            description="Get all tasks that are past their due date",
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
            name="get_tasks_by_tag",
            description="Get tasks filtered by a specific tag",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag": {
                        "type": "string",
                        "description": "Tag name to filter by (case-insensitive)",
                    },
                },
                "required": ["tag"],
            },
        ),
        Tool(
            name="get_all_tags",
            description="Get all unique tags used in tasks",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        # ==================== TASK MANAGEMENT TOOLS ====================
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
            name="create_task_with_subtasks",
            description="Create a new task with subtasks (checklist items)",
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
                    "subtasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "status": {"type": "integer", "enum": [0, 1]},
                            },
                            "required": ["title"],
                        },
                        "description": "List of subtasks. Each has 'title' and optional 'status' (0=pending, 1=done)",
                    },
                },
                "required": ["title", "subtasks"],
            },
        ),
        Tool(
            name="add_subtask",
            description="Add a subtask to an existing task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Parent task ID",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project ID where the task belongs",
                    },
                    "subtask_title": {
                        "type": "string",
                        "description": "Subtask title",
                    },
                },
                "required": ["task_id", "project_id", "subtask_title"],
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
        # ==================== PROJECT HANDLERS ====================
        if name == "get_projects":
            projects = await api.get_projects()
            if not projects:
                return [TextContent(type="text", text="No projects found.")]

            lines = [f"Found {len(projects)} project(s):\n"]
            for p in projects:
                lines.append(f"  • {format_project(p)}")
                lines.append(f"    ID: {p.get('id', 'N/A')}")

            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "get_project_by_id":
            project = await api.get_project_by_id(arguments["project_id"])
            return [TextContent(
                type="text",
                text=f"{format_project(project)}\nID: {project.get('id')}\n\n{json.dumps(project, indent=2)}",
            )]

        elif name == "get_project_with_data":
            data = await api.get_project_with_data(arguments["project_id"])
            project = data["project"]
            tasks = data["tasks"]
            columns = data.get("columns", [])

            lines = [f"📁 Project: {project.get('name', 'Untitled')}\n"]
            lines.append(f"Tasks: {len(tasks)}")
            if columns:
                lines.append(f"Columns: {', '.join(c.get('name', '') for c in columns)}")
            lines.append("\n" + format_tasks_list(tasks, show_subtasks=True))

            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "create_project":
            project = await api.create_project(
                name=arguments["name"],
                color=arguments.get("color", "#4772FA"),
                view_mode=arguments.get("view_mode", "list"),
                kind=arguments.get("kind", "TASK"),
            )
            return [TextContent(
                type="text",
                text=f"✅ Project created: {project.get('name', 'Untitled')}\nID: {project.get('id', 'N/A')}",
            )]

        elif name == "update_project":
            project = await api.update_project(
                project_id=arguments["project_id"],
                name=arguments.get("name"),
                color=arguments.get("color"),
                view_mode=arguments.get("view_mode"),
            )
            return [TextContent(type="text", text=f"✅ Project updated: {project.get('name', 'Untitled')}")]

        elif name == "delete_project":
            await api.delete_project(arguments["project_id"])
            return [TextContent(type="text", text="🗑️ Project deleted.")]

        # ==================== TASK QUERY HANDLERS ====================
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

        elif name == "get_overdue_tasks":
            tasks = await api.get_overdue_tasks()
            result = format_tasks_list(tasks)
            if tasks:
                result = f"⚠️ OVERDUE tasks ({len(tasks)}):\n\n{result}"
            else:
                result = "✅ No overdue tasks!"
            return [TextContent(type="text", text=result)]

        elif name == "get_high_priority_tasks":
            min_priority = arguments.get("min_priority", 3)
            tasks = await api.get_tasks_by_priority(min_priority)
            priority_label = {1: "Low+", 3: "Medium+", 5: "High"}.get(min_priority, "")
            result = format_tasks_list(tasks)
            if tasks:
                result = f"🎯 {priority_label} priority tasks:\n\n{result}"
            return [TextContent(type="text", text=result)]

        elif name == "get_tasks_by_tag":
            tag = arguments["tag"]
            tasks = await api.get_tasks_by_tag(tag)
            result = format_tasks_list(tasks)
            if tasks:
                result = f"🏷️ Tasks with tag '{tag}':\n\n{result}"
            else:
                result = f"No tasks found with tag '{tag}'"
            return [TextContent(type="text", text=result)]

        elif name == "get_all_tags":
            tags = await api.get_all_tags()
            if tags:
                return [TextContent(type="text", text=f"🏷️ All tags ({len(tags)}):\n\n" + "\n".join(f"  • {t}" for t in tags))]
            else:
                return [TextContent(type="text", text="No tags found.")]

        # ==================== TASK MANAGEMENT HANDLERS ====================
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

        elif name == "create_task_with_subtasks":
            task = await api.create_task_with_subtasks(
                title=arguments["title"],
                project_id=arguments.get("project_id"),
                content=arguments.get("content"),
                priority=arguments.get("priority", 0),
                due_date=arguments.get("due_date"),
                subtasks=arguments.get("subtasks", []),
            )
            subtask_count = len(arguments.get("subtasks", []))
            return [TextContent(
                type="text",
                text=f"✅ Task created: {task.get('title', 'Untitled')} with {subtask_count} subtask(s)\nID: {task.get('id', 'N/A')}",
            )]

        elif name == "add_subtask":
            task = await api.add_subtask(
                task_id=arguments["task_id"],
                project_id=arguments["project_id"],
                subtask_title=arguments["subtask_title"],
            )
            return [TextContent(
                type="text",
                text=f"✅ Subtask added: {arguments['subtask_title']}",
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
