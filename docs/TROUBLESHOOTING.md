# Troubleshooting

Use this guide when the MCP server does not start, Claude does not show the
TickTick tools, or authentication fails.

Do not paste real TickTick access tokens, OAuth secrets, `.env` files, or
private task data into public issues.

## `TICKTICK_ACCESS_TOKEN is required`

The server did not receive a TickTick access token.

Check these items:

- The token exists in your MCP client config under `env.TICKTICK_ACCESS_TOKEN`,
  or in a local `.env` file when running from source.
- The environment variable name is exactly `TICKTICK_ACCESS_TOKEN`.
- The token value is not wrapped in placeholder text such as
  `your_access_token_here`.
- You restarted the MCP client after changing its config.
- If you installed with `pip`, the server may not read the repository `.env`;
  put the token in the MCP client config instead.

## Claude Desktop Does Not Show TickTick Tools

Claude Desktop only loads MCP servers after restart.

Check these items:

- The config file is valid JSON.
- The server name is under `mcpServers`.
- The command is available on your system path.
- If using `python -m ticktick_mcp.server`, the package is installed in the same
  Python environment that Claude starts.
- If running from source, `cwd` points to the repository path you cloned.
- Restart Claude Desktop completely after editing the config.

For a pip install, a minimal config is:

```json
{
  "mcpServers": {
    "ticktick": {
      "command": "python",
      "args": ["-m", "ticktick_mcp.server"],
      "env": {
        "TICKTICK_ACCESS_TOKEN": "replace_with_your_token"
      }
    }
  }
}
```

For a source checkout, install the package first:

```bash
python -m pip install -e .
```

Then use the same `python -m ticktick_mcp.server` command from the environment
where the package is installed.

## Testing Without Exposing Private Tasks

When reporting a bug or testing a change:

- Use fake task titles and fake project names in screenshots and logs.
- Prefer mocked tests for API behavior.
- Do not paste full MCP client config if it contains credentials.
- Redact task content, project IDs, access tokens, OAuth client IDs, and OAuth
  client secrets.

Safe local checks:

```bash
python -m compileall src
ruff check .
pytest
```

These checks do not need a real TickTick token.

## API Calls Fail After Setup

If the server starts but TickTick API calls fail:

- Confirm the token was created for the same TickTick account you expect to use.
- Confirm the OAuth app has task read/write permissions.
- Create a new token if the old one was revoked or expired.
- Check whether the same call works with a small test task instead of private
  production tasks.

If you open an issue, include the package version, Python version, MCP client,
and sanitized error text.
