"""Tests for TickTick API client."""

import pytest
from unittest.mock import AsyncMock, patch

# Note: These are example tests. You'll need to set up proper mocking
# for the API calls since we don't want to make real API calls in tests.


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
