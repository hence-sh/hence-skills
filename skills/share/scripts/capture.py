#!/usr/bin/env python3
"""Capture screenshots of web applications using Playwright.

Usage:
    python capture.py <url> [--output <filename>] [--wait <ms>]
    python capture.py <url> --multi home.png,features.png,about.png

Examples:
    python capture.py http://localhost:3000
    python capture.py http://localhost:3000 --output hero.png
    python capture.py http://localhost:3000 --output hero.png --wait 3000
"""

import argparse
import subprocess
import sys


def run_playwright(args: list[str]) -> int:
    """Run a playwright-cli command, returning the exit code."""
    cmd = ["npx", "playwright-cli", *args]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"playwright-cli error: {result.stderr.strip()}", file=sys.stderr)
        return result.returncode
    except FileNotFoundError:
        print("Error: npx not found. Ensure Node.js is installed.", file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired:
        print("Error: Playwright command timed out.", file=sys.stderr)
        return 1


def capture_screenshot(url: str, output: str = "screenshot.png", wait_ms: int = 2000) -> bool:
    """Open a URL, wait, take a screenshot, and close the browser."""
    print(f"Opening {url}...")
    if run_playwright(["open", url]) != 0:
        return False

    import time
    time.sleep(wait_ms / 1000)

    print(f"Capturing screenshot → {output}")
    if run_playwright(["screenshot", f"--filename={output}"]) != 0:
        return False

    run_playwright(["close"])
    print(f"Saved: {output}")
    return True


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
