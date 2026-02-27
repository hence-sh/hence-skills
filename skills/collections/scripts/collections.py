#!/usr/bin/env python3
"""Manage Hence collections — list, create, add/remove items, search within.

Usage:
    python collections.py list
    python collections.py create --name "Board Name" [--description "..."] [--private]
    python collections.py view <collection-id>
    python collections.py search <collection-id> "query"
    python collections.py add --collection <id> --project <id>
    python collections.py remove --collection <id> --project <id>
    python collections.py update <collection-id> [--name "..."] [--description "..."] [--public|--private]
    python collections.py delete <collection-id>
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


def api_request(method: str, path: str, body: dict | None = None) -> dict:
    """Make an authenticated API request and return the parsed response."""
    token = get_token()
    url = f"{API_BASE}{path}"

    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        try:
            error_data = json.loads(error_body)
            msg = error_data.get("error", error_body)
        except json.JSONDecodeError:
            msg = error_body
        print(f"Error: API returned {e.code} — {msg}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Could not reach API — {e.reason}", file=sys.stderr)
        sys.exit(1)


# ── Commands ────────────────────────────────────────────────────────


def cmd_list(args):
    """List all collections for the authenticated user."""
    data = api_request("GET", "/collections")
    collections = data.get("data", [])

    if not collections:
        print("You have no collections yet. Create one with: python collections.py create --name \"My Board\"")
        return

    print("Your collections:\n")
    for c in collections:
        item_count = len(c.get("collection_items", []))
        visibility = "public" if c.get("is_public", True) else "private"
        print(f"  {c['name']}  ({item_count} items, {visibility})")
        if c.get("description"):
            print(f"    {c['description']}")
        print(f"    ID: {c['id']}")
        print()


def cmd_create(args):
    """Create a new collection."""
    body = {
        "name": args.name,
        "description": args.description or "",
        "is_public": not args.private,
    }
    data = api_request("POST", "/collections", body)
    collection = data.get("data", {})
    print(f"Collection created: {collection.get('name', args.name)}")
    print(f"  ID: {collection.get('id', '?')}")


def cmd_view(args):
    """View a collection and its projects."""
    data = api_request("GET", f"/collections/{args.collection_id}")
    collection = data.get("data", {})
    items = collection.get("items", [])

    print(f"## {collection.get('name', 'Untitled')}")
    if collection.get("description"):
        print(f"  {collection['description']}")
    print(f"  {collection.get('total', len(items))} projects\n")

    if not items:
        print("  No projects in this collection yet.")
        return

    for item in items:
        post = item.get("post")
        if not post:
            continue
        title = post.get("title", "Untitled")
        pitch = post.get("one_liner", "")
        pid = post.get("id", "?")
        link = f"https://hence.sh/p/{pid}"

        agents = post.get("post_agents", [])
        agent_names = ", ".join(
            a.get("agents", {}).get("name", "") for a in agents if a.get("agents")
        )

        print(f"  ### {title}")
        if pitch:
            print(f"    {pitch}")
        if agent_names:
            print(f"    Built with: {agent_names}")
        print(f"    Link: {link}")
        print()


def cmd_search(args):
    """Search within a collection by keyword."""
    query = urllib.parse.quote(args.query)
    data = api_request("GET", f"/collections/{args.collection_id}?q={query}")
    collection = data.get("data", {})
    items = collection.get("items", [])
    total = collection.get("total", len(items))

    print(f"Search results in \"{collection.get('name', 'collection')}\" for \"{args.query}\":\n")

    if not items:
        print("  No matching projects found.")
        return

    for item in items:
        post = item.get("post")
        if not post:
            continue
        title = post.get("title", "Untitled")
        pitch = post.get("one_liner", "")
        pid = post.get("id", "?")
        link = f"https://hence.sh/p/{pid}"

        print(f"  ### {title}")
        if pitch:
            print(f"    {pitch}")
        print(f"    Link: {link}")
        print()

    print(f"Found {total} matching projects.")


def cmd_add(args):
    """Add a project to a collection."""
    body = {
        "collection_id": args.collection,
        "post_id": args.project,
    }
    api_request("POST", "/collections/items", body)
    print(f"Project {args.project} added to collection {args.collection}.")


def cmd_remove(args):
    """Remove a project from a collection."""
    cid = urllib.parse.quote(args.collection)
    pid = urllib.parse.quote(args.project)
    api_request("DELETE", f"/collections/items?collection_id={cid}&post_id={pid}")
    print(f"Project {args.project} removed from collection {args.collection}.")


def cmd_update(args):
    """Update a collection's name, description, or visibility."""
    body = {}
    if args.name is not None:
        body["name"] = args.name
    if args.description is not None:
        body["description"] = args.description
    if args.public:
        body["is_public"] = True
    elif args.private:
        body["is_public"] = False

    if not body:
        print("Nothing to update. Provide --name, --description, --public, or --private.")
        sys.exit(1)

    data = api_request("PATCH", f"/collections/{args.collection_id}", body)
    collection = data.get("data", {})
    print(f"Collection updated: {collection.get('name', '?')}")


def cmd_delete(args):
    """Delete a collection."""
    api_request("DELETE", f"/collections/{args.collection_id}")
    print(f"Collection {args.collection_id} deleted.")


# ── CLI ─────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Manage Hence collections")
    parser.add_argument("--json", action="store_true", help="Output raw JSON (where applicable)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="List your collections")

    # create
    p_create = subparsers.add_parser("create", help="Create a new collection")
    p_create.add_argument("--name", required=True, help="Collection name")
    p_create.add_argument("--description", default="", help="Collection description")
    p_create.add_argument("--private", action="store_true", help="Make collection private")

    # view
    p_view = subparsers.add_parser("view", help="View a collection's projects")
    p_view.add_argument("collection_id", help="Collection UUID")

    # search
    p_search = subparsers.add_parser("search", help="Search within a collection")
    p_search.add_argument("collection_id", help="Collection UUID")
    p_search.add_argument("query", help="Search keywords")

    # add
    p_add = subparsers.add_parser("add", help="Add a project to a collection")
    p_add.add_argument("--collection", required=True, help="Collection UUID")
    p_add.add_argument("--project", required=True, help="Project UUID")

    # remove
    p_remove = subparsers.add_parser("remove", help="Remove a project from a collection")
    p_remove.add_argument("--collection", required=True, help="Collection UUID")
    p_remove.add_argument("--project", required=True, help="Project UUID")

    # update
    p_update = subparsers.add_parser("update", help="Update a collection")
    p_update.add_argument("collection_id", help="Collection UUID")
    p_update.add_argument("--name", default=None, help="New name")
    p_update.add_argument("--description", default=None, help="New description")
    p_update.add_argument("--public", action="store_true", help="Make public")
    p_update.add_argument("--private", action="store_true", help="Make private")

    # delete
    p_delete = subparsers.add_parser("delete", help="Delete a collection")
    p_delete.add_argument("collection_id", help="Collection UUID")

    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "create": cmd_create,
        "view": cmd_view,
        "search": cmd_search,
        "add": cmd_add,
        "remove": cmd_remove,
        "update": cmd_update,
        "delete": cmd_delete,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
