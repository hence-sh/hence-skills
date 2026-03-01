#!/usr/bin/env python3
"""Manage screenshots on an existing Hence project.

Usage:
    python scripts/screenshots.py <project_id> list
    python scripts/screenshots.py <project_id> add --file hero.png [--caption "Caption"]
    python scripts/screenshots.py <project_id> update <screenshot_id> [--file new.png] [--caption "New caption"]
    python scripts/screenshots.py <project_id> remove <screenshot_id>
    python scripts/screenshots.py <project_id> reorder <id1> <id2> <id3> ...
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


def api_request(method: str, url: str, token: str, body: bytes = None, content_type: str = None) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    if content_type:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
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


def build_multipart(fields: dict, files: list[tuple[str, str]]) -> tuple[bytes, str]:
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


def cmd_list(token: str, project_id: str):
    url = f"{API_BASE}/{project_id}/screenshots"
    result = api_request("GET", url, token)
    screenshots = result.get("data", [])
    if not screenshots:
        print("No screenshots found.")
        return
    for s in screenshots:
        caption_display = f'"{s["caption"]}"' if s["caption"] else '""'
        print(f"{s['id']}  pos={s['position']}  {caption_display}  {s['url']}")


def cmd_add(token: str, project_id: str, file_path: str, caption: str):
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    fields = {"caption": caption} if caption else {}
    files = [("file", file_path)]
    body, content_type = build_multipart(fields, files)
    url = f"{API_BASE}/{project_id}/screenshots"
    result = api_request("POST", url, token, body, content_type)
    s = result.get("data", {})
    print(f"Added screenshot: {s.get('id')}  pos={s.get('position')}  \"{s.get('caption', '')}\"")


def cmd_update(token: str, project_id: str, screenshot_id: str, file_path: str = None, caption: str = None):
    fields = {}
    if caption is not None:
        fields["caption"] = caption
    files = []
    if file_path:
        if not os.path.isfile(file_path):
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        files.append(("file", file_path))
    if not fields and not files:
        print("Error: Provide at least --file or --caption.", file=sys.stderr)
        sys.exit(1)
    body, content_type = build_multipart(fields, files)
    url = f"{API_BASE}/{project_id}/screenshots/{screenshot_id}"
    result = api_request("PATCH", url, token, body, content_type)
    s = result.get("data", {})
    print(f"Updated: {s.get('id')}  pos={s.get('position')}  \"{s.get('caption', '')}\"")


def cmd_remove(token: str, project_id: str, screenshot_id: str):
    url = f"{API_BASE}/{project_id}/screenshots/{screenshot_id}"
    result = api_request("DELETE", url, token)
    print(f"Removed: {result.get('data', {}).get('deleted', screenshot_id)}")


def cmd_reorder(token: str, project_id: str, order: list[str]):
    body = json.dumps({"order": order}).encode()
    url = f"{API_BASE}/{project_id}/screenshots/reorder"
    result = api_request("POST", url, token, body, "application/json")
    print(f"Reordered: {' '.join(result.get('data', {}).get('reordered', order))}")


def main():
    parser = argparse.ArgumentParser(
        description="Manage screenshots on a Hence project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("project_id", help="UUID of the project")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List all screenshots")

    add_p = subparsers.add_parser("add", help="Add a screenshot")
    add_p.add_argument("--file", required=True, help="Path to image file")
    add_p.add_argument("--caption", default="", help="Caption text")

    update_p = subparsers.add_parser("update", help="Update a screenshot")
    update_p.add_argument("screenshot_id", help="UUID of the screenshot")
    update_p.add_argument("--file", default=None, help="New image file")
    update_p.add_argument("--caption", default=None, help="New caption text")

    remove_p = subparsers.add_parser("remove", help="Remove a screenshot")
    remove_p.add_argument("screenshot_id", help="UUID of the screenshot")

    reorder_p = subparsers.add_parser("reorder", help="Reorder screenshots")
    reorder_p.add_argument("ids", nargs="+", help="Screenshot UUIDs in desired order")

    args = parser.parse_args()
    token = get_token()

    if args.command == "list":
        cmd_list(token, args.project_id)
    elif args.command == "add":
        cmd_add(token, args.project_id, args.file, args.caption)
    elif args.command == "update":
        cmd_update(token, args.project_id, args.screenshot_id, args.file, args.caption)
    elif args.command == "remove":
        cmd_remove(token, args.project_id, args.screenshot_id)
    elif args.command == "reorder":
        cmd_reorder(token, args.project_id, args.ids)


if __name__ == "__main__":
    main()
