---
name: hence-share
description: Share a completed project to the Hence gallery (hence.sh) so the world can see what you built with AI. Use when the user has finished building something and wants to share it, post it to Hence, showcase their work, or upload screenshots of their project. Triggers on phrases like "share this on Hence", "post to Hence", "upload my project", or "let's publish this".
compatibility: Requires Python 3.8+. Screenshot capture requires Node.js and npx (for Playwright).
---

# Hence Share

> **Install from your project root directory.** Running `npx skills add` from a subdirectory will install into the wrong location.

Package and publish a project to the Hence gallery with screenshots, metadata, and attribution.

## Workflow

### 1. Authenticate

Check for existing credentials. If none found, start the device flow:

```bash
python scripts/auth.py --check
```

If the check fails, run the device flow:

```bash
python scripts/auth.py
```

The script will print a URL and a one-time code. **Before running the command, tell the user** they'll need to:
1. Open the URL in their browser
2. Log in to Hence if they aren't already (via GitHub or Google)
3. Enter the code shown in the terminal

The script will wait and automatically complete once the user approves. No further action is needed from the agent after that.

For CI/CD environments, pass an API key directly:

```bash
python scripts/auth.py <api-key>
```

### 2. Gather metadata

Fetch valid slugs before assembling the project:

```bash
python scripts/fetch_metadata.py topics
python scripts/fetch_metadata.py agents
python scripts/fetch_metadata.py models
```

Pass `--json` for raw JSON when further processing is needed. See [references/api.md](references/api.md) for response schemas.

Ask the user:
- Which **topics** fit their project (pick from the list)
- Which **agent and model** they used (pick from the lists)
- A **title**, **one-liner** pitch, and optionally a **backstory** for the description

### 3. Capture screenshots

Up to 5 screenshots (1 primary + 4 additional).

**For web apps** — use the capture script:

```bash
python scripts/capture.py http://localhost:3000 --output hero.png
python scripts/capture.py http://localhost:3000/features --output features.png
```

**For non-web projects** — ask the user for screenshot file paths.

### 4. Share

```bash
python scripts/share.py \
  --title "My Project" \
  --one-liner "A short pitch" \
  --description "The backstory..." \
  --screenshot hero.png \
  --screenshot features.png \
  --topics '["cli", "productivity"]' \
  --agents '[{"slug": "claude_code", "model_slug": "claude-sonnet-4"}]' \
  --url "https://myproject.dev"
```

The script shows a review summary and asks for confirmation before uploading.

Pass `--yes` to skip the confirmation prompt when running non-interactively.

### 5. Update an existing project

```bash
python scripts/update.py <project-id> --title "New Title" --one-liner "Updated pitch"
```

### 6. Inspired-by linking

If the user found inspiration via `hence-search` and you stored a project ID with `save_memory`, include it:

```bash
python scripts/share.py ... --inspired-by <project-id>
```

## API details

See [references/api.md](references/api.md) for full endpoint documentation, field formats, and error codes.
