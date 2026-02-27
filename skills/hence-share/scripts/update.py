#!/usr/bin/env python3
"""Update an existing project on Hence.

Usage:
    python update.py <project_id> [--title "New Title"] [--one-liner "New pitch"] \
        [--screenshot new.png] [--topics '["cli"]'] [--agents '[...]']

Only pass the fields you want to update.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(__file__))
from auth import get_token

API_BASE = os.environ.get("HENCE_API_URL", "https://hence.sh") + "/api/projects"


def build_multipart(fields: dict, files: list[tuple[str, str]]) -> tuple[bytes, str]:
    """Build a multipart/form-data body."""
    import uuid
    boundary = f"----SkillBoundary{uuid.uuid4().hex}"

    parts = []
    for name, value in fields.items():
        if value is None:
            continue
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n"
        )

    for field_name, filepath in files:
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            data = f.read()
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
        )
        parts.append(data)
        parts.append(b"\r\n")

    parts.append(f"--{boundary}--\r\n")

    body = b""
    for part in parts:
        body += part.encode() if isinstance(part, str) else part

    return body, f"multipart/form-data; boundary={boundary}"


def update_project(
    token: str,
    project_id: str,
    title: str = "",
    one_liner: str = "",
    screenshot: str = "",
    topics: str = "",
    agents: str = "",
) -> dict:
    """Send a PATCH request to update a project."""
    fields = {}
    if title:
        fields["title"] = title
    if one_liner:
        fields["one_liner"] = one_liner
    if topics:
        fields["topics"] = topics
    if agents:
        fields["agents"] = agents

    files = []
    if screenshot and os.path.isfile(screenshot):
        files.append(("primary_screenshot", screenshot))

    if not fields and not files:
        print("Error: Nothing to update. Pass at least one field.", file=sys.stderr)
        sys.exit(1)

    body, content_type = build_multipart(fields, files)

    url = f"{API_BASE}/{project_id}"
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": content_type,
        },
        method="PATCH",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"Error: API returned {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Could not reach API — {e.reason}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Update an existing Hence project")
    parser.add_argument("project_id", help="UUID of the project to update")
    parser.add_argument("--title", default="", help="New title")
    parser.add_argument("--one-liner", default="", help="New pitch")
    parser.add_argument("--screenshot", default="", help="New primary screenshot path")
    parser.add_argument("--topics", default="", help='JSON array of topic slugs')
    parser.add_argument("--agents", default="", help='JSON array of agent objects')
    args = parser.parse_args()

    token = get_token()

    result = update_project(
        token=token,
        project_id=args.project_id,
        title=args.title,
        one_liner=args.one_liner,
        screenshot=args.screenshot,
        topics=args.topics,
        agents=args.agents,
    )

    print(f"Updated successfully: https://hence.sh/p/{args.project_id}")


if __name__ == "__main__":
    main()
