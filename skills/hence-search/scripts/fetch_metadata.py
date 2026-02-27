#!/usr/bin/env python3
"""Fetch Hence metadata: topics, agents, and models.

Usage:
    python fetch_metadata.py topics
    python fetch_metadata.py agents
    python fetch_metadata.py models
    python fetch_metadata.py all
"""

import json
import os
import sys
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(__file__))
from auth import get_token

API_BASE = os.environ.get("HENCE_API_URL", "https://hence.sh") + "/api"

ENDPOINTS = {
    "topics": f"{API_BASE}/topics",
    "agents": f"{API_BASE}/agents",
    "models": f"{API_BASE}/models",
}


def fetch(endpoint: str) -> list:
    """Fetch a list from a Hence API endpoint."""
    token = get_token()
    req = urllib.request.Request(
        endpoint,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data if isinstance(data, list) else data.get("data", [])
    except urllib.error.HTTPError as e:
        print(f"Error: API returned {e.code} for {endpoint}", file=sys.stderr)
        return []
    except urllib.error.URLError as e:
        print(f"Error: Could not reach {endpoint} — {e.reason}", file=sys.stderr)
        return []


def format_items(items: list, kind: str) -> str:
    """Format metadata items for display."""
    if not items:
        return f"No {kind} found."

    lines = [f"Available {kind}:"]
    for item in items:
        slug = item.get("slug", item.get("name", "?"))
        name = item.get("name", slug)
        if slug != name:
            lines.append(f"  - {name} ({slug})")
        else:
            lines.append(f"  - {slug}")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in (*ENDPOINTS, "all"):
        print("Usage: python fetch_metadata.py {topics|agents|models|all}")
        sys.exit(1)

    kind = sys.argv[1]

    if kind == "all":
        for k, url in ENDPOINTS.items():
            items = fetch(url)
            print(format_items(items, k))
            print()
    else:
        items = fetch(ENDPOINTS[kind])
        if "--json" in sys.argv:
            print(json.dumps(items, indent=2))
        else:
            print(format_items(items, kind))


if __name__ == "__main__":
    main()
