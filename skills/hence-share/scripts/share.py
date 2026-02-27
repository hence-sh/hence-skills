#!/usr/bin/env python3
"""Share a project to the Hence gallery.

Usage:
    python share.py --title "Name" --one-liner "Pitch" --screenshot hero.png \
        [--description "..."] [--topics '["cli"]'] [--agents '[{"slug":"claude_code","model_slug":"claude-sonnet-4"}]'] \
        [--url "https://..."] [--deployment-status "public"] [--inspired-by <id>] \
        [--screenshot feature.png] [--yes]

Screenshots: Pass --screenshot multiple times (max 5). The first is the primary screenshot.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

# Reuse auth helper
sys.path.insert(0, os.path.dirname(__file__))
from auth import get_token

API_URL = os.environ.get("HENCE_API_URL", "https://hence.sh") + "/api/projects"


def build_multipart(fields: dict, files: list[tuple[str, str]]) -> tuple[bytes, str]:
    """Build a multipart/form-data body from fields and files.

    fields: dict of name → string value
    files: list of (field_name, file_path) tuples
    Returns: (body_bytes, content_type)
    """
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
        if isinstance(part, str):
            body += part.encode()
        else:
            body += part

    return body, f"multipart/form-data; boundary={boundary}"


def share_project(
    token: str,
    title: str,
    one_liner: str,
    screenshots: list[str],
    description: str = "",
    topics: str = "[]",
    agents: str = "[]",
    url: str = "",
    deployment_status: str = "public",
    inspired_by_id: str = "",
) -> dict:
    """Upload a project to Hence and return the response."""
    fields = {
        "title": title,
        "one_liner": one_liner,
        "description": description,
        "topics": topics,
        "agents": agents,
        "url": url,
        "deployment_status": deployment_status,
    }
    if inspired_by_id:
        fields["inspired_by_id"] = inspired_by_id

    files = []
    for i, path in enumerate(screenshots[:5]):
        if not os.path.isfile(path):
            print(f"Error: Screenshot not found: {path}", file=sys.stderr)
            sys.exit(1)
        if i == 0:
            files.append(("primary_screenshot", path))
        else:
            files.append((f"screenshot_{i}", path))

    body, content_type = build_multipart(fields, files)

    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": content_type,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"Error: API returned {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Could not reach API — {e.reason}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Share a project to Hence")
    parser.add_argument("--title", required=True, help="Project title")
    parser.add_argument("--one-liner", required=True, help="Short pitch")
    parser.add_argument("--screenshot", action="append", required=True, dest="screenshots", help="Screenshot path (repeat for multiple, max 5)")
    parser.add_argument("--description", default="", help="Full project description")
    parser.add_argument("--topics", default="[]", help='JSON array of topic slugs, e.g. \'["cli","react"]\'')
    parser.add_argument("--agents", default="[]", help='JSON array of agent objects, e.g. \'[{"slug":"claude_code","model_slug":"claude-sonnet-4"}]\'')
    parser.add_argument("--url", default="", help="Project URL")
    parser.add_argument("--deployment-status", default="public", help="Deployment status: local, closed, or public (default: public)")
    parser.add_argument("--inspired-by", default="", help="UUID of inspiring project")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    # Validate JSON args
    for field, value in [("topics", args.topics), ("agents", args.agents)]:
        try:
            json.loads(value)
        except json.JSONDecodeError:
            print(f"Error: --{field} must be valid JSON. Got: {value}", file=sys.stderr)
            sys.exit(1)

    token = get_token()

    # Show review summary
    print("--- Review Project ---")
    print(f"  Title:        {args.title}")
    print(f"  One-liner:    {args.one_liner}")
    if args.description:
        print(f"  Description:  {args.description[:100]}...")
    print(f"  Topics:       {args.topics}")
    print(f"  Agents:       {args.agents}")
    print(f"  Screenshots:  {', '.join(args.screenshots)}")
    if args.url:
        print(f"  URL:          {args.url}")
    print("----------------------")

    if not args.yes:
        confirm = input("Share this project? (y/N): ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            sys.exit(0)

    result = share_project(
        token=token,
        title=args.title,
        one_liner=args.one_liner,
        screenshots=args.screenshots,
        description=args.description,
        topics=args.topics,
        agents=args.agents,
        url=args.url,
        deployment_status=args.deployment_status,
        inspired_by_id=args.inspired_by,
    )

    project_id = result.get("data", {}).get("id", "unknown")
    print(f"\nShared successfully! View at: https://hence.sh/p/{project_id}")


if __name__ == "__main__":
    main()
