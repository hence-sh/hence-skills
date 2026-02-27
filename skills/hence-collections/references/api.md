# Hence Collections API Reference

## List Collections

**Endpoint:** `GET https://hence.sh/api/collections`

**Authentication:** `Authorization: Bearer <token>` header required.

**Response:**

```json
{
  "data": [
    {
      "id": "uuid",
      "creator_id": "uuid",
      "name": "My Board",
      "description": "Favorite CLI tools",
      "is_public": true,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z",
      "collection_items": [
        { "post_id": "uuid" }
      ]
    }
  ]
}
```

## Create Collection

**Endpoint:** `POST https://hence.sh/api/collections`

**Authentication:** `Authorization: Bearer <token>` header required.

**Content-Type:** `application/json`

| Field         | Type    | Required | Default | Description               |
|---------------|---------|----------|---------|---------------------------|
| `name`        | string  | Yes      | —       | Collection name           |
| `description` | string  | No       | `""`    | Collection description    |
| `is_public`   | boolean | No       | `true`  | Whether publicly visible  |

**Response (200):**

```json
{
  "data": {
    "id": "uuid",
    "name": "My Board",
    "description": "...",
    "is_public": true,
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

## Get Collection (with search)

**Endpoint:** `GET https://hence.sh/api/collections/<id>`

**Authentication:** `Authorization: Bearer <token>` header required.

| Parameter | Type   | Default | Description                                        |
|-----------|--------|---------|----------------------------------------------------|
| `q`       | string | `""`    | Search keywords to filter projects in the collection |

**Response:**

```json
{
  "data": {
    "id": "uuid",
    "name": "My Board",
    "description": "...",
    "is_public": true,
    "total": 3,
    "items": [
      {
        "id": "uuid",
        "added_at": "2025-01-01T00:00:00Z",
        "post": {
          "id": "uuid",
          "title": "Project Name",
          "one_liner": "Short pitch",
          "description": "Full description",
          "primary_screenshot_url": "https://...",
          "url": "https://...",
          "created_at": "2025-01-01T00:00:00Z",
          "creator": { "id": "uuid", "display_name": "...", "avatar_url": "..." },
          "post_topics": [{ "topics": { "name": "CLI", "slug": "cli" } }],
          "post_agents": [{ "agents": { "name": "Claude Code", "slug": "claude_code" }, "models": { "name": "Claude Sonnet 4", "slug": "claude-sonnet-4" } }]
        }
      }
    ]
  }
}
```

When `q` is provided, only items whose project title, one-liner, or description contain the keyword are returned.

## Update Collection

**Endpoint:** `PATCH https://hence.sh/api/collections/<id>`

**Authentication:** `Authorization: Bearer <token>` header required.

**Content-Type:** `application/json`

All fields are optional — only send what you want to change:

| Field         | Type    | Description               |
|---------------|---------|---------------------------|
| `name`        | string  | New collection name       |
| `description` | string  | New description           |
| `is_public`   | boolean | Change visibility         |

**Response (200):**

```json
{
  "data": {
    "id": "uuid",
    "name": "Updated Name",
    "description": "...",
    "is_public": true
  }
}
```

## Delete Collection

**Endpoint:** `DELETE https://hence.sh/api/collections/<id>`

**Authentication:** `Authorization: Bearer <token>` header required.

Deletes the collection and all its item associations. The projects themselves are not deleted.

**Response (200):**

```json
{ "success": true }
```

## Add Project to Collection

**Endpoint:** `POST https://hence.sh/api/collections/items`

**Authentication:** `Authorization: Bearer <token>` header required.

**Content-Type:** `application/json`

| Field           | Type   | Required | Description         |
|-----------------|--------|----------|---------------------|
| `collection_id` | string | Yes      | Collection UUID     |
| `post_id`       | string | Yes      | Project UUID to add |

If the project is already in the collection, this is a no-op (upsert).

**Response (200):**

```json
{ "success": true }
```

## Remove Project from Collection

**Endpoint:** `DELETE https://hence.sh/api/collections/items`

**Authentication:** `Authorization: Bearer <token>` header required.

| Parameter       | Type   | Required | Description             |
|-----------------|--------|----------|-------------------------|
| `collection_id` | string | Yes      | Collection UUID         |
| `post_id`       | string | Yes      | Project UUID to remove  |

**Response (200):**

```json
{ "success": true }
```

**Errors:** 400 (missing params), 401 (auth), 404 (collection not found), 500 (server).
