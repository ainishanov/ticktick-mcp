# TickTick MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for [TickTick](https://ticktick.com/) task management. This enables AI assistants like Claude to interact with your TickTick tasks.

## Features

### Project Management
- 📁 **Get Projects** - List all your TickTick projects/lists
- 📁 **Get Project by ID** - Get specific project details
- 📁 **Get Project with Data** - Get project with all tasks and kanban columns
- ➕ **Create Project** - Create new projects with custom colors and view modes
- ✏️ **Update Project** - Modify project settings
- 🗑️ **Delete Project** - Remove projects

### Task Queries
- ✅ **Get Tasks** - Retrieve tasks from all projects or a specific one
- 📅 **Today's Tasks** - Get tasks due today
- ⚠️ **Overdue Tasks** - Get tasks past their due date
- 🎯 **Priority Filter** - Get high/medium priority tasks
- 🏷️ **Filter by Tag** - Get tasks with specific tags
- 🏷️ **Get All Tags** - List all unique tags

### Task Management
- ➕ **Create Tasks** - Add new tasks with title, priority, due date
- ➕ **Create with Subtasks** - Add tasks with checklist items
- ➕ **Add Subtask** - Add subtask to existing task
- ✔️ **Complete Tasks** - Mark tasks as done
- ✏️ **Update Tasks** - Modify existing tasks
- 🗑️ **Delete Tasks** - Remove tasks

## Installation

### Option 1: pip install (recommended)

```bash
pip install ticktick-mcp
```

### Option 2: From source

```bash
git clone https://github.com/ainishanov/ticktick-mcp.git
cd ticktick-mcp
pip install -e .
```

## Setup

### 1. Get TickTick API Access Token

1. Go to [TickTick Developer Portal](https://developer.ticktick.com/)
2. Create a new application
3. Complete OAuth2 flow to get your access token
4. Copy the access token

### 2. Configure Environment

Create a `.env` file in the project directory:

```bash
cp .env.example .env
```

Edit `.env` and add your token:

```
TICKTICK_ACCESS_TOKEN=your_access_token_here
```

### 3. Configure Claude Desktop

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ticktick": {
      "command": "python",
      "args": ["-m", "ticktick_mcp.server"],
      "env": {
        "TICKTICK_ACCESS_TOKEN": "your_access_token_here"
      }
    }
  }
}
```

Or if installed from source:

```json
{
  "mcpServers": {
    "ticktick": {
      "command": "python",
      "args": ["-m", "ticktick_mcp.server"],
      "cwd": "/path/to/ticktick-mcp/src",
      "env": {
        "TICKTICK_ACCESS_TOKEN": "your_access_token_here"
      }
    }
  }
}
```

### Claude Code (CLI)

Add to `~/.mcp.json` (macOS/Linux) or `%USERPROFILE%\.mcp.json` (Windows):

```json
{
  "mcpServers": {
    "ticktick": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "ticktick_mcp.server"],
      "cwd": "/path/to/ticktick-mcp/src",
      "env": {
        "TICKTICK_ACCESS_TOKEN": "your_access_token_here"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

After configuration, restart Claude Desktop to load the MCP server.

## Usage Examples

Once configured, you can ask Claude:

- "What tasks do I have today?"
- "Show me all high priority tasks"
- "Create a task 'Review PR #123' with high priority due tomorrow"
- "Mark task ID xxx in project yyy as complete"
- "What projects do I have in TickTick?"

## Available Tools

### Project Tools
| Tool | Description |
|------|-------------|
| `get_projects` | List all TickTick projects |
| `get_project_by_id` | Get specific project by ID |
| `get_project_with_data` | Get project with tasks and columns |
| `create_project` | Create a new project |
| `update_project` | Update project settings |
| `delete_project` | Delete a project |

### Task Query Tools
| Tool | Description |
|------|-------------|
| `get_tasks` | Get tasks (all or by project) |
| `get_today_tasks` | Get tasks due today |
| `get_overdue_tasks` | Get tasks past due date |
| `get_high_priority_tasks` | Get high/medium priority tasks |
| `get_tasks_by_tag` | Get tasks by tag |
| `get_all_tags` | List all unique tags |

### Task Management Tools
| Tool | Description |
|------|-------------|
| `create_task` | Create a new task |
| `create_task_with_subtasks` | Create task with checklist |
| `add_subtask` | Add subtask to existing task |
| `complete_task` | Mark task as complete |
| `update_task` | Update task details |
| `delete_task` | Delete a task |

## Priority Levels

| Value | Level | Emoji |
|-------|-------|-------|
| 0 | None | ⚪ |
| 1 | Low | 🔵 |
| 3 | Medium | 🟡 |
| 5 | High | 🔴 |

## Development

```bash
# Clone repo
git clone https://github.com/ainishanov/ticktick-mcp.git
cd ticktick-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .
```

## OAuth2 Token Generation

If you need to generate an access token programmatically, here's a helper script:

```python
import httpx

CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
REDIRECT_URI = "http://localhost:8080/callback"

# Step 1: Get authorization URL
auth_url = f"https://ticktick.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=tasks:read tasks:write"
print(f"Open this URL in browser:\n{auth_url}")

# Step 2: After redirect, exchange code for token
code = input("Enter the code from redirect URL: ")

response = httpx.post(
    "https://ticktick.com/oauth/token",
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    },
)

print(response.json())
# Save the access_token to your .env file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- [TickTick](https://ticktick.com/) for their API
