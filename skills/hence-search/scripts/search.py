#!/usr/bin/env python3
"""Search the Hence gallery for projects.

Usage:
    python search.py <query> [--topic <slug>] [--limit <n>] [--offset <n>]

Examples:
    python search.py "productivity cli"
    python search.py "react" --topic web --limit 5
    python search.py "" --topic game --offset 20
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error

sys.path.insert(0, os.path.dirname(__file__))
from auth import get_token

API_BASE = os.environ.get("HENCE_API_URL", "https://hence.sh") + "/api"


def search(query: str, topic: str = "", limit: int = 20, offset: int = 0) -> dict:
    """Search the Hence gallery and return results as a dict."""
    params = {"limit": str(limit), "offset": str(offset)}
    if query:
        params["q"] = query
    if topic:
        params["topic"] = topic

    token = get_token()
    url = f"{API_BASE}/search?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Error: API returned {e.code}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Could not reach API — {e.reason}", file=sys.stderr)
        sys.exit(1)


def format_results(data: dict) -> str:
    """Format search results for display."""
    projects = data.get("data", data.get("projects", []))
    if not projects:
        return "No projects found."

    lines = []
    for p in projects:
        pid = p.get("id", "?")
        title = p.get("title", "Untitled")
        pitch = p.get("one_liner", "")
        link = f"https://hence.sh/p/{pid}"

        agents = p.get("agents", [])
        agent_names = ", ".join(a.get("name", a.get("slug", "")) for a in agents) if agents else ""

        lines.append(f"## {title}")
        if pitch:
            lines.append(f"  {pitch}")
        if agent_names:
            lines.append(f"  Built with: {agent_names}")
        lines.append(f"  Link: {link}")
        lines.append("")

    total = data.get("total", len(projects))
    lines.append(f"Showing {len(projects)} of {total} results.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search the Hence gallery")
    parser.add_argument("query", nargs="?", default="", help="Search keywords")
    parser.add_argument("--topic", default="", help="Filter by topic slug")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    parser.add_argument("--offset", type=int, default=0, help="Pagination offset")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    data = search(args.query, topic=args.topic, limit=args.limit, offset=args.offset)

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(format_results(data))


if __name__ == "__main__":
    main()
