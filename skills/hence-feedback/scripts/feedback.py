#!/usr/bin/env python3
"""Submit feedback about the Hence experience.

Usage:
    python feedback.py --source user --category user_experience --rating 5
    python feedback.py --source agent --category agent_experience --aspect auth_flow --comment "..."
    python feedback.py --source both --category user_experience --rating 4 --comment "..."
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(__file__))
from auth import get_token

API_BASE = os.environ.get("HENCE_API_URL", "https://hence.sh") + "/api"

VALID_SOURCES = ["user", "agent", "both"]
VALID_CATEGORIES = ["user_experience", "agent_experience"]
VALID_UX_ASPECTS = ["onboarding", "discovery", "sharing", "collections", "navigation", "overall"]
VALID_AGENT_ASPECTS = ["auth_flow", "api_ergonomics", "skill_install", "error_messages", "documentation", "overall"]


def submit_feedback(payload: dict) -> dict:
    """POST feedback to the Hence API."""
    token = get_token()
    url = f"{API_BASE}/feedback"
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
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


def main():
    parser = argparse.ArgumentParser(description="Submit feedback about Hence")
    parser.add_argument(
        "--source",
        required=True,
        choices=VALID_SOURCES,
        help="Who is submitting: user, agent, or both",
    )
    parser.add_argument(
        "--category",
        required=True,
        choices=VALID_CATEGORIES,
        help="Feedback category: user_experience or agent_experience",
    )
    parser.add_argument(
        "--aspect",
        default=None,
        help=(
            "Specific aspect (user_experience: onboarding, discovery, sharing, collections, "
            "navigation, overall | agent_experience: auth_flow, api_ergonomics, skill_install, "
            "error_messages, documentation, overall)"
        ),
    )
    parser.add_argument(
        "--rating",
        type=int,
        default=None,
        choices=[1, 2, 3, 4, 5],
        help="Rating from 1 to 5",
    )
    parser.add_argument(
        "--comment",
        default=None,
        help="Free-form comment (max 2000 characters)",
    )
    parser.add_argument(
        "--agent-name",
        default=None,
        help="Name of the agent submitting the feedback",
    )
    parser.add_argument(
        "--skill-context",
        default=None,
        help="Skill name providing context for this feedback",
    )

    args = parser.parse_args()

    if args.rating is None and not args.comment:
        print("Error: At least one of --rating or --comment is required.", file=sys.stderr)
        sys.exit(1)

    if args.comment and len(args.comment) > 2000:
        print("Error: --comment must be 2000 characters or less.", file=sys.stderr)
        sys.exit(1)

    if args.aspect:
        valid_aspects = VALID_UX_ASPECTS if args.category == "user_experience" else VALID_AGENT_ASPECTS
        if args.aspect not in valid_aspects:
            print(
                f"Error: --aspect must be one of: {', '.join(valid_aspects)}",
                file=sys.stderr,
            )
            sys.exit(1)

    payload = {
        "source": args.source,
        "category": args.category,
    }
    if args.aspect is not None:
        payload["aspect"] = args.aspect
    if args.rating is not None:
        payload["rating"] = args.rating
    if args.comment is not None:
        payload["comment"] = args.comment
    if args.agent_name is not None:
        payload["agent_name"] = args.agent_name
    if args.skill_context is not None:
        payload["skill_context"] = args.skill_context

    result = submit_feedback(payload)
    feedback = result.get("data", {})
    print("Feedback submitted successfully.")
    if feedback.get("id"):
        print(f"  ID: {feedback['id']}")


if __name__ == "__main__":
    main()
