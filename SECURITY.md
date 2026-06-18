# Security Policy

## Reporting a vulnerability

Please report security issues privately by emailing the repository owner or by
opening a GitHub security advisory if available.

Do not open a public issue with access tokens, OAuth secrets, private task data,
or MCP client configuration that contains credentials.

## Credential handling

TickTick MCP needs a TickTick OAuth access token. Keep it in your MCP client
configuration or a local `.env` file. Do not commit credentials to the
repository.

If a token is exposed, revoke or rotate it in TickTick before continuing.
