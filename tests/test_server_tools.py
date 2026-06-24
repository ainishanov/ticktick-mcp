from unittest.mock import AsyncMock, patch

import pytest
from mcp.types import TextContent

from ticktick_mcp.server import call_tool


# ==========FIXTURES & SETUP ==========================
@pytest.fixture
def mock_api():
    """Fixture to patch get_api and return a fully mocked TickTickAPI instance."""
    with patch("ticktick_mcp.server.get_api") as mock_get_api:
        api_instance=AsyncMock()
        mock_get_api.return_value=api_instance
        yield api_instance

# ==============COVERAGE: PROJECT QUERY TOOL (get_projects)=============
@pytest.mark.asyncio
async def test_call_tool_get_projects_success(mock_api):
    """Verify get_projects tool properly structures and routes project data."""
    mock_api.get_projects.return_value=[
        {"id": "p1", "name": "Work", "color": "#4772FA", "viewMode": "list"}
    ]

    response=await call_tool("get_projects", {})

    assert len(response) == 1
    assert isinstance(response[0], TextContent)
    assert "Found 1 project(s):" in response[0].text
    assert "Work (list) #4772FA" in response[0].text
    assert "ID: p1" in response[0].text
    mock_api.get_projects.assert_called_once()



# ===========COVERAGE: TASK QUERY TOOL (get_today_tasks)================
@pytest.mark.asyncio
async def test_call_tool_get_today_tasks_empty(mock_api):
    """Verify task query tool handles an empty state response cleanly."""
    # Setup mock to return an empty list of tasks for today
    mock_api.get_today_tasks.return_value=[]

    response=await call_tool("get_today_tasks", {})

    assert len(response)==1
    assert "No tasks due today!" in response[0].text
    mock_api.get_today_tasks.assert_called_once()


# =========COVERAGE: TASK MUTATION TOOL (create_task)====================================
@pytest.mark.asyncio
async def test_call_tool_create_task_success(mock_api):
    """Verify task mutation tools successfully forward arguments and confirm creation."""
    mock_api.create_task.return_value={
        "id": "t123",
        "title": "Review PR comments"
    }

    arguments = {
        "title": "Review PR comments",
        "priority": 3,
        "due_date": "2026-06-24"
    }

    response = await call_tool("create_task", arguments)

    assert len(response)==1
    assert "✅ Task created: Review PR comments" in response[0].text
    assert "ID: t123" in response[0].text

    # to ensure all user args were unpacked and forwarded down to the API layer perfectly
    mock_api.create_task.assert_called_once_with(
        title="Review PR comments",
        project_id=None,
        content=None,
        priority=3,
        due_date="2026-06-24"
    )


# ===================COVERAGE: UNKNOWN TOOL ROUTING BRANCH=========================================
@pytest.mark.asyncio
async def test_call_tool_unknown_name(mock_api):
    """Verify executing an invalid tool name returns an informative message instead of crashing."""
    response=await call_tool("completely_invalid_tool_name", {})

    assert len(response)==1
    assert "Unknown tool: completely_invalid_tool_name" in response[0].text


# =====================COVERAGE: GLOBAL EXCEPTION HANDLING=====================================
@pytest.mark.asyncio
async def test_call_tool_exception_handling(mock_api):
    """Verify that backend exceptions are caught and wrapped in an error block gracefully."""
    # Force the mock API client to throw a connection error or bad token issue
    mock_api.get_projects.side_effect=Exception("API Connection Timeout")

    response=await call_tool("get_projects", {})

    assert len(response) == 1
    # Check that it caught the error internally and turned it into an error notification message
    assert " Error: API Connection Timeout" in response[0].text
