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
