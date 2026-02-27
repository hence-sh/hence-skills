#!/usr/bin/env python3
"""Capture screenshots of web applications using Playwright.

Usage:
    python capture.py <url> [--output <filename>] [--wait <ms>]

Examples:
    python capture.py http://localhost:3000
    python capture.py http://localhost:3000 --output hero.png
    python capture.py http://localhost:3000 --output hero.png --wait 3000
"""

import argparse
import subprocess
import sys


def capture_screenshot(url: str, output: str = "screenshot.png", wait_ms: int = 2000) -> bool:
    """Take a screenshot of a URL using the Playwright CLI."""
    cmd = ["npx", "playwright", "screenshot", "--wait-for-timeout", str(wait_ms), url, output]
    print(f"Capturing {url} → {output}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"playwright error: {result.stderr.strip()}", file=sys.stderr)
            return False
        print(f"Saved: {output}")
        return True
    except FileNotFoundError:
        print("Error: npx not found. Ensure Node.js is installed.", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("Error: Playwright command timed out.", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Capture web screenshots via Playwright")
    parser.add_argument("url", help="URL to capture")
    parser.add_argument("--output", default="screenshot.png", help="Output filename (default: screenshot.png)")
    parser.add_argument("--wait", type=int, default=2000, help="Wait time in ms after page load (default: 2000)")
    args = parser.parse_args()

    success = capture_screenshot(args.url, output=args.output, wait_ms=args.wait)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
