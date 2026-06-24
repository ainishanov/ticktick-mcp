# Contributing

Thanks for helping improve TickTick MCP.

## Good first contributions

Good first issues should be small, testable, and safe to review:

- Add tests for pure Python helpers.
- Improve README setup steps or troubleshooting notes.
- Improve error messages returned by MCP tools.
- Add focused TickTick API response fixtures.

Avoid changes that require real TickTick credentials in CI.

## Local setup

```bash
git clone https://github.com/ainishanov/ticktick-mcp.git
cd ticktick-mcp
python -m venv venv
python -m pip install -e ".[dev]"
```

On Windows, use `.\venv\Scripts\python.exe -m pip install -e ".[dev]"`.

## Checks

Run these before opening a pull request:

```bash
python -m compileall src
ruff check .
pytest
```

Tests must not call the real TickTick API. Mock HTTP calls or API wrapper methods.

## Secrets and private data

Never commit:

- TickTick access tokens
- OAuth client secrets
- `.env` files
- private task titles, descriptions, or project names
- MCP client config files containing credentials

Use fake IDs and fake task content in tests and docs.

## Releasing

Maintainers should follow the [release checklist](docs/RELEASING.md) when publishing a new version to PyPI.
