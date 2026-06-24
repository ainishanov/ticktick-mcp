# TickTick MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/ainishanov/ticktick-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/ainishanov/ticktick-mcp/actions/workflows/ci.yml)

Connect AI assistants to TickTick.

TickTick MCP is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for [TickTick](https://ticktick.com/). It lets Claude and other MCP clients read projects, find tasks, create tasks, and complete work from chat.

## What You Can Do

- Ask what is due today.
- Find overdue or high-priority tasks.
- Create tasks and checklist items.
- Update, complete, or delete tasks.
- Manage TickTick projects.

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

### 3. Configure MCP clients

`pip install` adds `ticktick-mcp` to your Python environment, so `cwd` is typically not required.
For source checkouts, set `cwd` to `/path/to/ticktick-mcp/src` so Python can import `ticktick_mcp` from the local source tree.

#### 3a. Claude Desktop

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\Claude Desktop\claude_desktop_config.json`

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

If you run from source:

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

#### 3b. Claude Code (CLI)

Add to `~/.mcp.json` (macOS/Linux) or `%USERPROFILE%\.mcp.json` (Windows):

```json
{
  "mcpServers": {
    "ticktick": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "ticktick_mcp.server"],
      "env": {
        "TICKTICK_ACCESS_TOKEN": "your_access_token_here"
      }
    }
  }
}
```

From source:

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

#### 3c. Cursor

Add a new MCP entry to Cursor’s config (often `~/.cursor/mcp.json`):

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

#### 3d. Continue

Add to Continue’s MCP config file (for example, `~/.continue/config.json`):

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

#### 3e. Generic stdio-compatible MCP config

Most MCP clients accept a similar shape. Use the same block format and place it in
your client’s MCP server configuration area:

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

### 4. Restart your MCP client

After configuration, restart the MCP client to load the server.

If the tools do not appear or the server reports an auth error, see
[Troubleshooting](docs/TROUBLESHOOTING.md).

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

Contributions are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and avoid committing access tokens, OAuth secrets, `.env` files, or private task data.

Good first contributions are small tests, docs improvements, focused error-message improvements, or mocked TickTick API fixtures.

Maintainers releasing a new version should follow the [release checklist](docs/RELEASING.md).

## Security

Do not open public issues with credentials or private task data. See [SECURITY.md](SECURITY.md).

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- [TickTick](https://ticktick.com/) for their API
