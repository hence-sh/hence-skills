#!/usr/bin/env python3
"""Authenticate with the Hence API.

Supports two modes:
  - Device flow (interactive): prints a code, user approves in browser
  - API key (CI/CD): pass a key directly

Usage:
    python auth.py                  # Start device flow (interactive)
    python auth.py <token>          # Save API key (for CI/CD)
    python auth.py --check          # Verify credentials exist
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

CONFIG_DIR = os.path.expanduser("~/.hence")
TOKEN_FILE = os.path.join(CONFIG_DIR, "token")
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, "credentials")

API_BASE = os.environ.get("HENCE_API_URL", "https://hence.sh")


def save_token(token: str) -> None:
    """Save an API key to the legacy token file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        f.write(token.strip())
    print("Authenticated successfully. API key saved to ~/.hence/token")


def load_token() -> str:
    """Load and return the stored token (legacy), or exit with an error."""
    if not os.path.isfile(TOKEN_FILE):
        print(
            "Error: Not authenticated. Run auth.py first, or get a token at hence.sh/settings",
            file=sys.stderr,
        )
        sys.exit(1)
    with open(TOKEN_FILE) as f:
        token = f.read().strip()
    if not token:
        print("Error: Token file is empty. Run auth.py to set a new token.", file=sys.stderr)
        sys.exit(1)
    return token


def save_credentials(access_token: str, refresh_token: str, expires_in: int) -> None:
    """Save OAuth credentials to ~/.hence/credentials."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": int(time.time()) + expires_in,
    }
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(data, f)


def load_credentials() -> dict | None:
    """Load credentials file, or return None if missing/invalid."""
    if not os.path.isfile(CREDENTIALS_FILE):
        return None
    try:
        with open(CREDENTIALS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def refresh_access_token(refresh_token: str) -> dict | None:
    """Exchange a refresh token for a new access token."""
    url = f"{API_BASE}/api/auth/refresh"
    body = json.dumps({"refresh_token": refresh_token}).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data
    except (urllib.error.HTTPError, urllib.error.URLError):
        return None


def get_token() -> str:
    """Get a valid access token, refreshing if needed. Falls back to legacy token file."""
    creds = load_credentials()
    if creds:
        # Check if access token is still valid (with 60s buffer)
        if creds.get("expires_at", 0) > time.time() + 60:
            return creds["access_token"]
        # Try to refresh
        refresh = creds.get("refresh_token")
        if refresh:
            result = refresh_access_token(refresh)
            if result and "access_token" in result:
                save_credentials(
                    result["access_token"],
                    refresh,
                    result.get("expires_in", 3600),
                )
                return result["access_token"]
    # Fall back to legacy token
    return load_token()


def start_device_flow() -> None:
    """Initiate and complete the OAuth device flow."""
    url = f"{API_BASE}/api/auth/device"
    req = urllib.request.Request(url, data=b"", method="POST")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"Error starting device flow: {e.code} {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Could not reach API — {e.reason}", file=sys.stderr)
        sys.exit(1)

    user_code = data["user_code"]
    device_code = data["device_code"]
    verification_uri = data["verification_uri"]
    interval = data.get("interval", 5)
    expires_in = data.get("expires_in", 900)

    print()
    print("To authenticate, open this URL in your browser and enter the code:")
    print()
    print("If you're not already logged in, you'll be prompted to sign in first.")
    print()
    print(f"  URL:   {verification_uri}")
    print(f"  Code:  {user_code}")
    print()
    print("Waiting for authorization...", end="", flush=True)

    deadline = time.time() + expires_in
    token_url = f"{API_BASE}/api/auth/device/token"

    while time.time() < deadline:
        time.sleep(interval)
        print(".", end="", flush=True)

        body = json.dumps({"device_code": device_code}).encode()
        req = urllib.request.Request(
            token_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())
                # Success
                print(" done!")
                save_credentials(
                    result["access_token"],
                    result["refresh_token"],
                    result.get("expires_in", 3600),
                )
                print("Authenticated successfully. Credentials saved to ~/.hence/credentials")
                return
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            try:
                error_data = json.loads(error_body)
            except json.JSONDecodeError:
                error_data = {}

            error_code = error_data.get("error", "")
            if error_code == "authorization_pending":
                continue
            elif error_code == "expired_token":
                print("\nError: Code expired. Please try again.", file=sys.stderr)
                sys.exit(1)
            elif error_code == "access_denied":
                print("\nError: Authorization denied.", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"\nError polling for token: {e.code} {error_body}", file=sys.stderr)
                sys.exit(1)

    print("\nError: Timed out waiting for authorization.", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            creds = load_credentials()
            if creds:
                print("Credentials found (OAuth device flow).")
                return
            token = load_token()
            print(f"API key found: {token[:8]}...")
            return
        # Direct token/key argument — save as legacy
        save_token(sys.argv[1])
    else:
        start_device_flow()


if __name__ == "__main__":
    main()
