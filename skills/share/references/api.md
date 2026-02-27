# Hence Share API Reference

## Create Project

**Endpoint:** `POST https://hence.sh/api/projects`

**Authentication:** `Authorization: Bearer <token>` header required. Get a token at [hence.sh/settings](https://hence.sh/settings).

**Content-Type:** `multipart/form-data`

| Field                | Type   | Required | Description                                  |
|----------------------|--------|----------|----------------------------------------------|
| `title`              | string | Yes      | Project title                                |
| `one_liner`          | string | Yes      | Short pitch (one sentence)                   |
| `description`        | string | Yes      | Full backstory / details                     |
| `deployment_status`  | string | No       | `"local"`, `"closed"`, or `"public"`         |
| `url`                | string | Yes      | Project URL                                  |
| `primary_screenshot` | file   | Yes      | Main screenshot image                        |
| `screenshot_1`–`screenshot_4` | file | No | Up to 4 additional screenshots              |
| `topics`             | JSON   | No       | Array of topic slugs: `["cli","productivity"]`|
| `agents`             | JSON   | No       | Array of agent objects (see below)           |
| `inspired_by_id`     | string | No       | UUID of inspiring project                    |

**Agents format:**

```json
[
  { "slug": "claude_code", "model_slug": "claude-sonnet-4" }
]
```

**Response (201):**

```json
{
  "data": {
    "id": "uuid",
    "title": "...",
    "one_liner": "...",
    "primary_screenshot_url": "https://..."
  }
}
```

**Errors:** 400 (validation), 401 (auth), 500 (server).

## Update Project

**Endpoint:** `PATCH https://hence.sh/api/projects/<id>`

**Authentication:** Same as create.

**Content-Type:** `multipart/form-data`

All fields are optional — only send what you want to update:

| Field                | Type   | Description              |
|----------------------|--------|--------------------------|
| `title`              | string | New title                |
| `one_liner`          | string | New pitch                |
| `primary_screenshot` | file   | New primary screenshot   |
| `topics`             | JSON   | Replace topic slugs      |
| `agents`             | JSON   | Replace agent list       |

## Metadata Endpoints

Fetch valid slugs for topics, agents, and models:

- `GET https://hence.sh/api/topics` — all topics
- `GET https://hence.sh/api/agents` — all agents
- `GET https://hence.sh/api/models` — all models

All return `{ "data": [...] }` with objects containing `name` and `slug` fields.
