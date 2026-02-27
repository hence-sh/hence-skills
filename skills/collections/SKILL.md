---
name: collections
description: Manage your Hence collections (hence.sh) — create boards, save projects, and search within your saved items. Use when the user wants to organize projects, bookmark something on Hence, create a collection, or find a project they saved earlier. Triggers on phrases like "save this to my collection", "create a Hence collection", "search my saved projects", or "show my collections".
compatibility: Requires Python 3.8+.
---

# Hence Collections

Manage personal collections on Hence — create boards, add and remove projects, and search within saved items.

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

### 2. List collections

View all of the user's collections:

```bash
python scripts/collections.py list
```

### 3. Create a collection

```bash
python scripts/collections.py create --name "CLI Tools" --description "My favorite command-line projects"
```

Pass `--private` to make the collection visible only to the owner.

### 4. Add a project to a collection

```bash
python scripts/collections.py add --collection <collection-id> --project <project-id>
```

If the user found a project via `hence-search`, use the project ID from those results.

### 5. Remove a project from a collection

```bash
python scripts/collections.py remove --collection <collection-id> --project <project-id>
```

### 6. View a collection

Show all projects in a specific collection:

```bash
python scripts/collections.py view <collection-id>
```

### 7. Search within a collection

Find specific projects inside a collection by keyword:

```bash
python scripts/collections.py search <collection-id> "dashboard"
```

This searches across project titles, pitches, and descriptions within the collection.

### 8. Update a collection

```bash
python scripts/collections.py update <collection-id> --name "New Name" --description "Updated description"
```

### 9. Delete a collection

```bash
python scripts/collections.py delete <collection-id>
```

## API details

See [references/api.md](references/api.md) for full endpoint documentation, field formats, and error codes.
