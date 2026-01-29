"""OAuth2 flow to get TickTick access token."""

import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("TICKTICK_CLIENT_ID")
CLIENT_SECRET = os.getenv("TICKTICK_CLIENT_SECRET")
REDIRECT_URI = os.getenv("TICKTICK_REDIRECT_URI", "http://localhost:8080/callback")

# Store the code globally
auth_code = None


class OAuthHandler(BaseHTTPRequestHandler):
    """Handle OAuth2 callback."""

    def do_GET(self):
        global auth_code

        # Parse the callback URL
        parsed = urlparse(self.path)

        if parsed.path == "/callback":
            query = parse_qs(parsed.query)

            if "code" in query:
                auth_code = query["code"][0]

                # Send success response
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"""
                <html>
                <body style="font-family: Arial; text-align: center; padding-top: 50px;">
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
                """)
            else:
                error = query.get("error", ["Unknown error"])[0]
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(f"<h1>Error: {error}</h1>".encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress logging."""
        pass


def get_access_token():
    """Run OAuth2 flow and get access token."""
    global auth_code

    # Step 1: Build authorization URL
    auth_url = (
        f"https://ticktick.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=tasks:read tasks:write"
    )

    print("\n" + "=" * 60)
    print("TickTick OAuth2 Authorization")
    print("=" * 60)
    print("\nOpening browser for authorization...")
    print(f"\nIf browser doesn't open, visit:\n{auth_url}\n")

    # Open browser
    webbrowser.open(auth_url)

    # Start local server to catch callback
    print("Waiting for authorization callback...")
    server = HTTPServer(("localhost", 8080), OAuthHandler)

    while auth_code is None:
        server.handle_request()

    server.server_close()
    print(f"\nReceived authorization code: {auth_code[:10]}...")

    # Step 2: Exchange code for token
    print("\nExchanging code for access token...")

    response = httpx.post(
        "https://ticktick.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "scope": "tasks:read tasks:write",
        },
    )

    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")

        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"\nAccess Token:\n{access_token}\n")

        # Update .env file
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        with open(env_path, "r") as f:
            content = f.read()

        content = content.replace(
            "TICKTICK_ACCESS_TOKEN=",
            f"TICKTICK_ACCESS_TOKEN={access_token}"
        )

        with open(env_path, "w") as f:
            f.write(content)

        print("Token saved to .env file!")
        print("\nYou can now use the TickTick MCP server.")

        return access_token
    else:
        print(f"\nError: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    get_access_token()
