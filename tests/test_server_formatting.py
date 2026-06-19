from ticktick_mcp.server import format_project, format_task, format_tasks_list


# ===== TESTS FOR format_task =============================
def test_format_task_with_all_fields():
    """Verify format_task correctly serializes all fields including priority emojis."""
    mock_task={
        "title": "Making an Open Source PR",
        "_project_name": "Open Source",
        "dueDate": "2026-06-19T23:59:59+0000",
        "tags": ["python", "mcp"],
        "priority": 5,  #This should map to 🔴
    }

    result= format_task(mock_task)

    # Assert string structural components
    assert "🔴 Making an Open Source PR" in result
    assert "[Open Source]" in result
    assert "📅 2026-06-19" in result
    assert "🏷️ python, mcp" in result


def test_format_task_fallbacks():
    """Verify fallback values for completely empty dictionaries to prevent KeyErrors."""
    mock_empty_task={}

    result=format_task(mock_empty_task)

    # Defaults should kick in: priority=0 (⚪) and title="Untitled"
    assert "⚪ Untitled" in result
    assert "[" not in result
    assert "📅" not in result
    assert "🏷️" not in result


# ======== TESTS FOR format_tasks_list ======================
def test_format_tasks_list_empty():
    """Verify that an empty list returns the expected message."""
    assert format_tasks_list([]) == "No tasks found."

def test_format_tasks_list_with_subtasks():
    """Verify nested items rendering when show_subtasks is enabled."""
    mock_tasks=[
        {
            "id": "task_123",
            "projectId": "proj_abc",
            "title": "Main Task",
            "priority": 1,
            "items": [
                {"title": "Subtask One", "status": 1},   # 1 = Complete (✓)
                {"title": "Subtask Two", "status": 0},   # 0 = Pending (o)
            ]
        }
    ]

    # Run rendering with show_subtasks enabled
    result_with_subtasks=format_tasks_list(mock_tasks, show_subtasks=True)

    assert "Found 1 task(s):" in result_with_subtasks
    assert "🔵 Main Task" in result_with_subtasks
    assert "ID: task_123 | Project ID: proj_abc" in result_with_subtasks
    assert "✓ Subtask One" in result_with_subtasks
    assert "○ Subtask Two" in result_with_subtasks

    # Run rendering with show_subtasks disabled to verify omission
    result_hidden_subtasks=format_tasks_list(mock_tasks, show_subtasks=False)
    assert "✓ Subtask One" not in result_hidden_subtasks


#======= TESTS FOR format_project ===================================
def test_format_project_standard():
    """Verify project strings handle attributes properly."""
    mock_project={
        "name": "Work Inbox",
        "color": "#4772FA",
        "viewMode": "kanban"
    }

    result=format_project(mock_project)
    assert result=="📁 Work Inbox (kanban) #4772FA"


def test_format_project_fallbacks():
    """Verify formatting fallbacks when project data is partial."""
    mock_partial_project={}

    result=format_project(mock_partial_project)
    # name defaults to 'Untitled', viewMode defaults to 'list', color defaults to empty string
    assert result=="📁 Untitled (list) "
