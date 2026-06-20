"""Tests for TickTick API client."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
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
    async def test_request_raises_http_status_error(self, mock_api):
        """Test that API request errors raise HTTPStatusError for 4xx responses."""
        with patch("ticktick_mcp.api.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.request = httpx.Request("GET", "https://api.ticktick.com/open/v1/project")
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "401 Client Error: Unauthorized",
                request=mock_response.request,
                response=mock_response,
            )
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_cls.return_value = mock_client

            with pytest.raises(httpx.HTTPStatusError):
                await mock_api._request("GET", "/project")

    @pytest.mark.asyncio
    async def test_request_raises_http_status_error_for_server_error(self, mock_api):
        """Test that server-side API errors raise HTTPStatusError."""
        with patch("ticktick_mcp.api.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.request = httpx.Request("POST", "https://api.ticktick.com/open/v1/task")
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "500 Internal Server Error",
                request=mock_response.request,
                response=mock_response,
            )
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_cls.return_value = mock_client

            with pytest.raises(httpx.HTTPStatusError):
                await mock_api._request("POST", "/task")

    @pytest.mark.asyncio
    async def test_request_returns_empty_dict_for_204(self, mock_api):
        """Test that no-content API responses return an empty dict."""
        with patch("ticktick_mcp.api.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 204
            mock_response.raise_for_status.return_value = None
            mock_response.json = Mock()
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_cls.return_value = mock_client

            data = await mock_api._request("DELETE", "/project/proj1")

            assert data == {}
            mock_response.json.assert_not_called()
