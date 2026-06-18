"""Tests for TickTick API client."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest


class TestTickTickAPI:
    """Test cases for TickTickAPI class."""

    @pytest.fixture
    def mock_api(self):
        """Create a mock API instance."""
        with patch.dict("os.environ", {"TICKTICK_ACCESS_TOKEN": "test_token"}):
            from ticktick_mcp.api import TickTickAPI
            return TickTickAPI()

    def test_api_requires_token(self):
        """Test that API raises error without token."""
        with patch.dict("os.environ", {}, clear=True):
            from ticktick_mcp.api import TickTickAPI
            with pytest.raises(ValueError, match="TICKTICK_ACCESS_TOKEN is required"):
                TickTickAPI()

    def test_api_accepts_token(self):
        """Test that API accepts token from parameter."""
        from ticktick_mcp.api import TickTickAPI
        api = TickTickAPI(access_token="direct_token")
        assert api.access_token == "direct_token"

    @pytest.mark.asyncio
    async def test_get_projects(self, mock_api):
        """Test getting projects."""
        mock_response = [
            {"id": "proj1", "name": "Work"},
            {"id": "proj2", "name": "Personal"},
        ]

        with patch.object(mock_api, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            projects = await mock_api.get_projects()

            assert len(projects) == 2
            assert projects[0]["name"] == "Work"
            mock_request.assert_called_once_with("GET", "/project")

    @pytest.mark.asyncio
    async def test_create_task(self, mock_api):
        """Test creating a task."""
        mock_response = {"id": "task1", "title": "Test Task", "priority": 5}

        with patch.object(mock_api, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            task = await mock_api.create_task(
                title="Test Task",
                priority=5,
                due_date="2025-01-30",
            )

            assert task["title"] == "Test Task"
            assert task["priority"] == 5
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_task(self, mock_api):
        """Test completing a task."""
        with patch.object(mock_api, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {}
            await mock_api.complete_task(task_id="task1", project_id="proj1")

            mock_request.assert_called_once_with(
                "POST",
                "/project/proj1/task/task1/complete",
            )

    @pytest.mark.asyncio
    async def test_get_today_tasks(self, mock_api):
        """Returns only tasks due today."""
        today = datetime.now().strftime("%Y-%m-%d")
        tasks = [
            {"id": "t1", "title": "Today task", "dueDate": f"{today}T09:00:00+0000"},
            {"id": "t2", "title": "Tomorrow task", "dueDate": "2099-01-01T09:00:00+0000"},
            {"id": "t3", "title": "No due date"},
        ]

        with patch.object(mock_api, "get_all_tasks", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = tasks
            result = await mock_api.get_today_tasks()

            assert len(result) == 1
            assert result[0]["id"] == "t1"
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_overdue_tasks(self, mock_api):
        """Returns tasks with due date in the past and skips future/invalid dates."""
        past = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT12:00:00")
        future = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT12:00:00")

        tasks = [
            {"id": "t1", "title": "Past task", "dueDate": past},
            {"id": "t2", "title": "Future task", "dueDate": future},
            {"id": "t3", "title": "Bad date", "dueDate": "not-a-date"},
            {"id": "t4", "title": "No due date"},
        ]

        with patch.object(mock_api, "get_all_tasks", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = tasks
            result = await mock_api.get_overdue_tasks()

            assert [t["id"] for t in result] == ["t1"]
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_tags(self, mock_api):
        """Collects unique tags and returns sorted list."""
        tasks = [
            {"id": "t1", "tags": ["Work", "Urgent"]},
            {"id": "t2", "tags": ["Home", "Work"]},
            {"id": "t3", "tags": []},
            {"id": "t4"},
        ]

        with patch.object(mock_api, "get_all_tasks", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = tasks
            result = await mock_api.get_all_tags()

            assert result == ["Home", "Urgent", "Work"]
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_with_subtasks_builds_payload(self, mock_api):
        """Formats due date and checklist items when creating task with subtasks."""
        with patch.object(mock_api, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"id": "task1"}

            await mock_api.create_task_with_subtasks(
                title="Parent task",
                project_id="proj1",
                priority=3,
                due_date="2026-06-20",
                subtasks=[
                    {"title": "Sub 1"},
                    {"title": "Sub 2", "status": 1},
                ],
            )

            mock_request.assert_called_once_with(
                "POST",
                "/task",
                json={
                    "title": "Parent task",
                    "projectId": "proj1",
                    "priority": 3,
                    "dueDate": "2026-06-20T00:00:00+0000",
                    "items": [
                        {"title": "Sub 1", "status": 0, "sortOrder": 0},
                        {"title": "Sub 2", "status": 1, "sortOrder": 1},
                    ],
                },
            )
