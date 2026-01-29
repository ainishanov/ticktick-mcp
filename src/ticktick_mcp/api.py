"""TickTick API client with OAuth2 support."""

import os
from datetime import datetime
from typing import Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.ticktick.com/open/v1"


class TickTickAPI:
    """TickTick API client."""

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or os.getenv("TICKTICK_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError(
                "TICKTICK_ACCESS_TOKEN is required. "
                "Set it in .env file or pass directly."
            )
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[dict] = None,
    ) -> dict | list:
        """Make an authenticated request to TickTick API."""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=f"{BASE_URL}{endpoint}",
                headers=self.headers,
                json=json,
                timeout=30.0,
            )
            response.raise_for_status()
            if response.status_code == 204:
                return {}
            return response.json()

    async def get_projects(self) -> list[dict]:
        """Get all projects (lists) from TickTick."""
        return await self._request("GET", "/project")

    async def get_project_data(self, project_id: str) -> dict:
        """Get project data including all tasks."""
        return await self._request("GET", f"/project/{project_id}/data")

    async def get_all_tasks(self, project_id: Optional[str] = None) -> list[dict]:
        """
        Get all tasks, optionally filtered by project.

        Args:
            project_id: If provided, get tasks only from this project.
                       If None, get tasks from all projects.
        """
        if project_id:
            data = await self.get_project_data(project_id)
            return data.get("tasks", [])

        # Get tasks from all projects
        projects = await self.get_projects()
        all_tasks = []
        for project in projects:
            try:
                data = await self.get_project_data(project["id"])
                tasks = data.get("tasks", [])
                # Add project name to each task for context
                for task in tasks:
                    task["_project_name"] = project.get("name", "Unknown")
                all_tasks.extend(tasks)
            except httpx.HTTPStatusError:
                # Skip projects we can't access
                continue
        return all_tasks

    async def get_today_tasks(self) -> list[dict]:
        """Get tasks due today."""
        all_tasks = await self.get_all_tasks()
        today = datetime.now().strftime("%Y-%m-%d")

        today_tasks = []
        for task in all_tasks:
            due_date = task.get("dueDate", "")
            if due_date and due_date.startswith(today):
                today_tasks.append(task)

        return today_tasks

    async def get_tasks_by_priority(self, min_priority: int = 3) -> list[dict]:
        """
        Get tasks filtered by minimum priority.

        Priority levels in TickTick:
        - 0: None
        - 1: Low
        - 3: Medium
        - 5: High
        """
        all_tasks = await self.get_all_tasks()
        return [t for t in all_tasks if t.get("priority", 0) >= min_priority]

    async def create_task(
        self,
        title: str,
        project_id: Optional[str] = None,
        content: Optional[str] = None,
        priority: int = 0,
        due_date: Optional[str] = None,
    ) -> dict:
        """
        Create a new task.

        Args:
            title: Task title (required)
            project_id: Project/list ID. If None, goes to Inbox.
            content: Task description/notes
            priority: 0=None, 1=Low, 3=Medium, 5=High
            due_date: Due date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        """
        task_data = {"title": title}

        if project_id:
            task_data["projectId"] = project_id
        if content:
            task_data["content"] = content
        if priority:
            task_data["priority"] = priority
        if due_date:
            # Ensure proper format
            if len(due_date) == 10:  # YYYY-MM-DD
                due_date = f"{due_date}T00:00:00+0000"
            task_data["dueDate"] = due_date

        return await self._request("POST", "/task", json=task_data)

    async def update_task(
        self,
        task_id: str,
        project_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        priority: Optional[int] = None,
        due_date: Optional[str] = None,
    ) -> dict:
        """Update an existing task."""
        task_data = {"id": task_id, "projectId": project_id}

        if title:
            task_data["title"] = title
        if content is not None:
            task_data["content"] = content
        if priority is not None:
            task_data["priority"] = priority
        if due_date:
            if len(due_date) == 10:
                due_date = f"{due_date}T00:00:00+0000"
            task_data["dueDate"] = due_date

        return await self._request("POST", f"/task/{task_id}", json=task_data)

    async def complete_task(self, task_id: str, project_id: str) -> dict:
        """Mark a task as complete."""
        return await self._request(
            "POST",
            f"/project/{project_id}/task/{task_id}/complete",
        )

    async def delete_task(self, task_id: str, project_id: str) -> dict:
        """Delete a task."""
        return await self._request(
            "DELETE",
            f"/project/{project_id}/task/{task_id}",
        )

    # ==================== PROJECT MANAGEMENT ====================

    async def get_project_by_id(self, project_id: str) -> dict:
        """Get a specific project by ID."""
        projects = await self.get_projects()
        for project in projects:
            if project.get("id") == project_id:
                return project
        raise ValueError(f"Project {project_id} not found")

    async def get_project_with_data(self, project_id: str) -> dict:
        """Get project details along with tasks and columns."""
        project = await self.get_project_by_id(project_id)
        data = await self.get_project_data(project_id)
        return {
            "project": project,
            "tasks": data.get("tasks", []),
            "columns": data.get("columns", []),
        }

    async def create_project(
        self,
        name: str,
        color: str = "#4772FA",
        view_mode: str = "list",
        kind: str = "TASK",
    ) -> dict:
        """
        Create a new project.

        Args:
            name: Project name (required)
            color: Project color in hex format (default: '#4772FA')
            view_mode: 'list', 'kanban', or 'timeline' (default: 'list')
            kind: 'TASK' or 'NOTE' (default: 'TASK')
        """
        project_data = {
            "name": name,
            "color": color,
            "viewMode": view_mode,
            "kind": kind,
        }
        return await self._request("POST", "/project", json=project_data)

    async def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        color: Optional[str] = None,
        view_mode: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> dict:
        """Update an existing project."""
        project_data = {"id": project_id}

        if name:
            project_data["name"] = name
        if color:
            project_data["color"] = color
        if view_mode:
            project_data["viewMode"] = view_mode
        if kind:
            project_data["kind"] = kind

        return await self._request("POST", f"/project/{project_id}", json=project_data)

    async def delete_project(self, project_id: str) -> dict:
        """Delete a project."""
        return await self._request("DELETE", f"/project/{project_id}")

    # ==================== ADVANCED TASK QUERIES ====================

    async def get_overdue_tasks(self) -> list[dict]:
        """Get tasks that are past their due date."""
        all_tasks = await self.get_all_tasks()
        now = datetime.now()

        overdue_tasks = []
        for task in all_tasks:
            due_date = task.get("dueDate", "")
            if due_date:
                try:
                    # Parse due date (handle various formats)
                    due_str = due_date[:19].replace("T", " ")
                    if "+" in due_date:
                        due_str = due_date.split("+")[0]
                    task_due = datetime.fromisoformat(due_str)
                    if task_due < now:
                        overdue_tasks.append(task)
                except (ValueError, IndexError):
                    continue

        return overdue_tasks

    async def get_tasks_by_tag(self, tag: str) -> list[dict]:
        """
        Get tasks filtered by tag.

        Args:
            tag: Tag name to filter by (case-insensitive)
        """
        all_tasks = await self.get_all_tasks()
        tag_lower = tag.lower()

        tagged_tasks = []
        for task in all_tasks:
            task_tags = task.get("tags", [])
            if any(t.lower() == tag_lower for t in task_tags):
                tagged_tasks.append(task)

        return tagged_tasks

    async def get_all_tags(self) -> list[str]:
        """Get all unique tags from all tasks."""
        all_tasks = await self.get_all_tasks()
        tags = set()
        for task in all_tasks:
            task_tags = task.get("tags", [])
            tags.update(task_tags)
        return sorted(list(tags))

    # ==================== SUBTASKS ====================

    async def create_task_with_subtasks(
        self,
        title: str,
        project_id: Optional[str] = None,
        content: Optional[str] = None,
        priority: int = 0,
        due_date: Optional[str] = None,
        subtasks: Optional[list[dict]] = None,
    ) -> dict:
        """
        Create a new task with subtasks (checklist items).

        Args:
            title: Task title (required)
            project_id: Project/list ID. If None, goes to Inbox.
            content: Task description/notes
            priority: 0=None, 1=Low, 3=Medium, 5=High
            due_date: Due date in ISO format (YYYY-MM-DD)
            subtasks: List of subtask dicts with keys:
                - title (str): Subtask title (required)
                - status (int): 0=Normal, 1=Completed (default: 0)
        """
        task_data = {"title": title}

        if project_id:
            task_data["projectId"] = project_id
        if content:
            task_data["content"] = content
        if priority:
            task_data["priority"] = priority
        if due_date:
            if len(due_date) == 10:
                due_date = f"{due_date}T00:00:00+0000"
            task_data["dueDate"] = due_date

        # Add subtasks as checklist items
        if subtasks:
            items = []
            for i, subtask in enumerate(subtasks):
                item = {
                    "title": subtask.get("title", ""),
                    "status": subtask.get("status", 0),
                    "sortOrder": i,
                }
                items.append(item)
            task_data["items"] = items

        return await self._request("POST", "/task", json=task_data)

    async def add_subtask(
        self,
        task_id: str,
        project_id: str,
        subtask_title: str,
    ) -> dict:
        """
        Add a subtask to an existing task.

        Note: This fetches the task, adds the subtask, and updates.
        """
        # Get current task data
        data = await self.get_project_data(project_id)
        tasks = data.get("tasks", [])

        current_task = None
        for t in tasks:
            if t.get("id") == task_id:
                current_task = t
                break

        if not current_task:
            raise ValueError(f"Task {task_id} not found in project {project_id}")

        # Get existing items or create empty list
        items = current_task.get("items", [])

        # Add new subtask
        new_item = {
            "title": subtask_title,
            "status": 0,
            "sortOrder": len(items),
        }
        items.append(new_item)

        # Update task with new items
        task_data = {
            "id": task_id,
            "projectId": project_id,
            "items": items,
        }

        return await self._request("POST", f"/task/{task_id}", json=task_data)
