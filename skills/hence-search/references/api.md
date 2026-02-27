# Hence Search API Reference

## Search Projects

**Endpoint:** `GET https://hence.sh/api/search`

| Parameter | Type   | Default  | Description                                                    |
|-----------|--------|----------|----------------------------------------------------------------|
| `q`       | string | `""`     | Search keywords                                                |
| `topic`   | string | —        | Filter by topic slug                                           |
| `limit`   | int    | 20       | Max results to return                                          |
| `offset`  | int    | 0        | Pagination offset                                              |
| `sort`    | string | `recent` | Sort order: `recent` (newest first) or `relevant` (FTS rank, only meaningful when `q` is provided) |

**Response:**

```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Project Name",
      "one_liner": "Short pitch",
      "primary_screenshot_url": "https://...",
      "created_at": "2025-01-01T00:00:00Z",
      "creator": { "display_name": "...", "avatar_url": "..." },
      "topics": [{ "name": "...", "slug": "..." }]
    }
  ],
  "total": 42
}
```

## List Topics

**Endpoint:** `GET https://hence.sh/api/topics`

Returns all approved topics sorted alphabetically.

**Response:**

```json
{
  "data": [
    { "id": "uuid", "name": "CLI", "slug": "cli", "category": "what_its_built_with" }
  ]
}
```

Topic categories: `what_it_does`, `what_its_built_with`, `vibe`.

### Propose a Topic

**Endpoint:** `POST https://hence.sh/api/topics`

If a topic you need doesn't exist, propose it. Proposed topics won't appear in the list until reviewed and approved.

**Body (JSON):**

| Field      | Type   | Required | Description                                              |
|------------|--------|----------|----------------------------------------------------------|
| `slug`     | string | Yes      | URL-friendly identifier (e.g. `"rust"`)                  |
| `name`     | string | Yes      | Display name (e.g. `"Rust"`)                             |
| `category` | string | No       | `what_it_does`, `what_its_built_with`, or `vibe`         |

**Response (201):** `{ "data": { ... }, "proposed": true }`

If the slug already exists, the existing item is returned with `"proposed": false`.

## List Agents

**Endpoint:** `GET https://hence.sh/api/agents`

Returns all approved agents sorted alphabetically.

**Response:**

```json
{
  "data": [
    { "id": "uuid", "name": "Claude Code", "slug": "claude_code" }
  ]
}
```

### Propose an Agent

**Endpoint:** `POST https://hence.sh/api/agents`

**Body (JSON):**

| Field  | Type   | Required | Description                                  |
|--------|--------|----------|----------------------------------------------|
| `slug` | string | Yes      | URL-friendly identifier (e.g. `"my_agent"`)  |
| `name` | string | Yes      | Display name (e.g. `"My Agent"`)             |

**Response (201):** `{ "data": { ... }, "proposed": true }`

## List Models

**Endpoint:** `GET https://hence.sh/api/models`

Returns all approved models sorted alphabetically.

**Response:**

```json
{
  "data": [
    { "id": "uuid", "name": "Claude Sonnet 4", "slug": "claude-sonnet-4", "provider": "anthropic" }
  ]
}
```

### Propose a Model

**Endpoint:** `POST https://hence.sh/api/models`

**Body (JSON):**

| Field      | Type   | Required | Description                                        |
|------------|--------|----------|----------------------------------------------------|
| `slug`     | string | Yes      | URL-friendly identifier (e.g. `"my-model-v1"`)    |
| `name`     | string | Yes      | Display name (e.g. `"My Model v1"`)                |
| `provider` | string | No       | Provider name (e.g. `"Anthropic"`)                 |

**Response (201):** `{ "data": { ... }, "proposed": true }`
