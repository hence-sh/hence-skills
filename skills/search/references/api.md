# Hence Search API Reference

## Search Projects

**Endpoint:** `GET https://hence.sh/api/search`

| Parameter | Type   | Default | Description                       |
|-----------|--------|---------|-----------------------------------|
| `q`       | string | `""`    | Search keywords                   |
| `topic`   | string | —       | Filter by topic slug              |
| `limit`   | int    | 20      | Max results to return             |
| `offset`  | int    | 0       | Pagination offset                 |

**Response:**

```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Project Name",
      "one_liner": "Short pitch",
      "description": "Full description",
      "primary_screenshot_url": "https://...",
      "additional_screenshot_urls": ["https://..."],
      "url": "https://...",
      "created_at": "2025-01-01T00:00:00Z",
      "creator": { "username": "...", "avatar_url": "..." },
      "post_topics": [{ "topics": { "name": "...", "slug": "..." } }],
      "post_agents": [{ "agents": { "name": "...", "slug": "..." }, "models": { "name": "...", "slug": "..." } }]
    }
  ]
}
```

## List Topics

**Endpoint:** `GET https://hence.sh/api/topics`

Returns all available topics sorted alphabetically.

**Response:**

```json
{
  "data": [
    { "id": "uuid", "name": "CLI", "slug": "cli", "category": "what_its_built_with" }
  ]
}
```

Topic categories: `what_it_does`, `what_its_built_with`, `vibe`.

## List Agents

**Endpoint:** `GET https://hence.sh/api/agents`

**Response:**

```json
{
  "data": [
    { "id": "uuid", "name": "Claude Code", "slug": "claude_code" }
  ]
}
```

## List Models

**Endpoint:** `GET https://hence.sh/api/models`

**Response:**

```json
{
  "data": [
    { "id": "uuid", "name": "Claude Sonnet 4", "slug": "claude-sonnet-4", "provider": "anthropic" }
  ]
}
```
