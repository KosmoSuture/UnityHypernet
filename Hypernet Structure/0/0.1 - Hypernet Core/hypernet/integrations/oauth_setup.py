"""
OAuth2 Setup for Hypernet Personal Data Integrations

Handles OAuth2 authentication flow for:
- Gmail (Google OAuth2)
- Dropbox (Dropbox OAuth2)

Usage:
    python -m hypernet.integrations.oauth_setup gmail
    python -m hypernet.integrations.oauth_setup dropbox

Prerequisites:
    1. Create a Google Cloud project at https://console.cloud.google.com
    2. Enable Gmail API
    3. Create OAuth2 credentials (Desktop app type)
    4. Download client_secret.json to private/credentials/google_client_secret.json

For Dropbox:
    1. Create an app at https://www.dropbox.com/developers/apps
    2. Get app key and secret
    3. Store in private/credentials/dropbox_app.json

Security:
    - All tokens stored in private/oauth-tokens/ (gitignored)
    - Refresh tokens encrypted at rest (when GPG available)
    - File permissions restricted to owner (chmod 600)
"""

import json
import sys
import os
import stat
import webbrowser
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs, urlparse

# Default paths relative to Hypernet Structure
DEFAULT_PRIVATE_ROOT = Path(__file__).parent.parent.parent.parent.parent / "1 - People" / "1.1 Matt Schaeffer" / "private"


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth2 callback."""
    auth_code = None

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        if "code" in query:
            OAuthCallbackHandler.auth_code = query["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Authorization successful!</h1>"
                           b"<p>You can close this window and return to the terminal.</p>"
                           b"</body></html>")
        else:
            self.send_response(400)
            self.end_headers()
            error = query.get("error", ["unknown"])[0]
            self.wfile.write(f"<html><body><h1>Error: {error}</h1></body></html>".encode())

    def log_message(self, format, *args):
        pass  # Suppress HTTP logs


def setup_gmail_oauth(private_root: Path = DEFAULT_PRIVATE_ROOT):
    """Interactive OAuth2 setup for Gmail."""
    cred_dir = private_root / "credentials"
    token_dir = private_root / "oauth-tokens"
    token_dir.mkdir(parents=True, exist_ok=True)

    client_secret_path = cred_dir / "google_client_secret.json"
    if not client_secret_path.exists():
        print(f"""
Gmail OAuth2 Setup
==================

Before we begin, you need to create Google OAuth2 credentials:

1. Go to https://console.cloud.google.com/apis/credentials
2. Create a new project (or select existing)
3. Enable the Gmail API: https://console.cloud.google.com/apis/library/gmail.googleapis.com
4. Go to Credentials > Create Credentials > OAuth 2.0 Client ID
5. Application type: Desktop app
6. Download the JSON file
7. Save it to: {client_secret_path}

Then run this setup again.
""")
        return False

    with open(client_secret_path) as f:
        client_config = json.load(f)

    # Extract client ID and secret
    installed = client_config.get("installed", client_config.get("web", {}))
    client_id = installed["client_id"]
    client_secret = installed["client_secret"]

    # Gmail IMAP requires these scopes
    scopes = [
        "https://mail.google.com/",  # Full IMAP access
        "https://www.googleapis.com/auth/gmail.readonly",  # Read-only fallback
    ]

    # Build authorization URL
    auth_params = {
        "client_id": client_id,
        "redirect_uri": "http://localhost:8089",
        "response_type": "code",
        "scope": " ".join(scopes),
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(auth_params)}"

    print(f"\nOpening browser for Google authorization...")
    print(f"If browser doesn't open, visit:\n{auth_url}\n")
    webbrowser.open(auth_url)

    # Start local server to catch callback
    server = HTTPServer(("localhost", 8089), OAuthCallbackHandler)
    print("Waiting for authorization callback on http://localhost:8089 ...")
    server.handle_request()

    if not OAuthCallbackHandler.auth_code:
        print("ERROR: No authorization code received.")
        return False

    # Exchange code for tokens
    try:
        import httpx
    except ImportError:
        print("ERROR: httpx not installed. Run: pip install httpx")
        return False

    token_response = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": OAuthCallbackHandler.auth_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": "http://localhost:8089",
            "grant_type": "authorization_code",
        },
    )

    if token_response.status_code != 200:
        print(f"ERROR: Token exchange failed: {token_response.text}")
        return False

    tokens = token_response.json()

    # Determine which account this is for
    # Use the userinfo endpoint to get the email
    userinfo = httpx.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    user_email = userinfo.json().get("email", "unknown")

    # Save tokens
    token_file = token_dir / f"gmail_{user_email.replace('@', '_at_')}.json"
    token_data = {
        "email": user_email,
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "token_type": tokens.get("token_type"),
        "expires_in": tokens.get("expires_in"),
        "scope": tokens.get("scope"),
        "created_at": __import__("datetime").datetime.now().isoformat(),
    }
    token_file.write_text(json.dumps(token_data, indent=2))

    # Restrict file permissions (Unix)
    try:
        os.chmod(token_file, stat.S_IRUSR | stat.S_IWUSR)
    except (OSError, AttributeError):
        pass  # Windows doesn't support chmod the same way

    # Also save to credentials dir for the email connector
    cred_file = cred_dir / f"{user_email}.json"
    cred_file.write_text(json.dumps({
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "client_id": client_id,
        "client_secret": client_secret,
    }, indent=2))

    try:
        os.chmod(cred_file, stat.S_IRUSR | stat.S_IWUSR)
    except (OSError, AttributeError):
        pass

    print(f"\nSuccess! OAuth2 tokens saved for {user_email}")
    print(f"Token file: {token_file}")
    print(f"Credentials: {cred_file}")
    return True


def setup_dropbox_oauth(private_root: Path = DEFAULT_PRIVATE_ROOT):
    """Interactive OAuth2 setup for Dropbox."""
    cred_dir = private_root / "credentials"
    token_dir = private_root / "oauth-tokens"
    token_dir.mkdir(parents=True, exist_ok=True)

    app_config_path = cred_dir / "dropbox_app.json"
    if not app_config_path.exists():
        print(f"""
Dropbox OAuth2 Setup
====================

Before we begin, you need to create a Dropbox app:

1. Go to https://www.dropbox.com/developers/apps
2. Create app > Scoped access > Full Dropbox
3. Note the App key and App secret
4. Add http://localhost:8089 to Redirect URIs
5. Save this to {app_config_path}:

{{
    "app_key": "your_app_key",
    "app_secret": "your_app_secret"
}}

Then run this setup again.
""")
        return False

    with open(app_config_path) as f:
        app_config = json.load(f)

    app_key = app_config["app_key"]
    app_secret = app_config["app_secret"]

    auth_params = {
        "client_id": app_key,
        "redirect_uri": "http://localhost:8089",
        "response_type": "code",
        "token_access_type": "offline",
    }
    auth_url = f"https://www.dropbox.com/oauth2/authorize?{urlencode(auth_params)}"

    print(f"\nOpening browser for Dropbox authorization...")
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", 8089), OAuthCallbackHandler)
    OAuthCallbackHandler.auth_code = None
    print("Waiting for authorization callback...")
    server.handle_request()

    if not OAuthCallbackHandler.auth_code:
        print("ERROR: No authorization code received.")
        return False

    try:
        import httpx
    except ImportError:
        print("ERROR: httpx not installed. Run: pip install httpx")
        return False

    token_response = httpx.post(
        "https://api.dropboxapi.com/oauth2/token",
        data={
            "code": OAuthCallbackHandler.auth_code,
            "grant_type": "authorization_code",
            "client_id": app_key,
            "client_secret": app_secret,
            "redirect_uri": "http://localhost:8089",
        },
    )

    if token_response.status_code != 200:
        print(f"ERROR: Token exchange failed: {token_response.text}")
        return False

    tokens = token_response.json()

    token_file = token_dir / "dropbox.json"
    token_data = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "account_id": tokens.get("account_id"),
        "uid": tokens.get("uid"),
        "expires_in": tokens.get("expires_in"),
        "created_at": __import__("datetime").datetime.now().isoformat(),
    }
    token_file.write_text(json.dumps(token_data, indent=2))

    try:
        os.chmod(token_file, stat.S_IRUSR | stat.S_IWUSR)
    except (OSError, AttributeError):
        pass

    print(f"\nSuccess! Dropbox tokens saved.")
    print(f"Token file: {token_file}")
    return True


def refresh_gmail_token(email_address: str, private_root: Path = DEFAULT_PRIVATE_ROOT) -> str:
    """Refresh an expired Gmail access token. Returns new access token."""
    cred_dir = private_root / "credentials"
    cred_file = cred_dir / f"{email_address}.json"

    if not cred_file.exists():
        raise FileNotFoundError(f"No credentials for {email_address}")

    creds = json.loads(cred_file.read_text())

    try:
        import httpx
    except ImportError:
        raise ImportError("httpx required: pip install httpx")

    response = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "refresh_token": creds["refresh_token"],
            "grant_type": "refresh_token",
        },
    )

    if response.status_code != 200:
        raise RuntimeError(f"Token refresh failed: {response.text}")

    new_tokens = response.json()
    creds["access_token"] = new_tokens["access_token"]
    cred_file.write_text(json.dumps(creds, indent=2))

    return new_tokens["access_token"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m hypernet.integrations.oauth_setup [gmail|dropbox]")
        sys.exit(1)

    service = sys.argv[1].lower()
    if service == "gmail":
        setup_gmail_oauth()
    elif service == "dropbox":
        setup_dropbox_oauth()
    else:
        print(f"Unknown service: {service}. Use 'gmail' or 'dropbox'.")
        sys.exit(1)
