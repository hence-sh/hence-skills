# Hence Feedback API Reference

Base URL: `https://hence.sh/api`

All endpoints require authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <token>
```

---

## POST /feedback

Submit feedback about the Hence experience.

### Request body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source` | string | yes | Who is submitting: `user`, `agent`, or `both` |
| `category` | string | yes | `user_experience` or `agent_experience` |
| `aspect` | string | no | Specific area of focus (see valid values below) |
| `rating` | integer | no* | 1–5 stars |
| `comment` | string | no* | Free-form text, max 2000 characters |
| `agent_name` | string | no | Name of the agent submitting the feedback |
| `skill_context` | string | no | Skill providing context for this feedback |

\* At least one of `rating` or `comment` is required.

### Valid aspect values

**When `category` is `user_experience`:**
- `onboarding`
- `discovery`
- `sharing`
- `collections`
- `navigation`
- `overall`

**When `category` is `agent_experience`:**
- `auth_flow`
- `api_ergonomics`
- `skill_install`
- `error_messages`
- `documentation`
- `overall`

### Example request

```json
{
  "source": "agent",
  "category": "agent_experience",
  "aspect": "auth_flow",
  "rating": 5,
  "comment": "Device flow was seamless.",
  "agent_name": "claude-code",
  "skill_context": "hence-share"
}
```

### Response — 201 Created

```json
{
  "data": {
    "id": "uuid",
    "creator_id": "uuid",
    "source": "agent",
    "category": "agent_experience",
    "aspect": "auth_flow",
    "rating": 5,
    "comment": "Device flow was seamless.",
    "agent_name": "claude-code",
    "skill_context": "hence-share",
    "created_at": "2026-02-20T00:00:00.000Z"
  }
}
```

### Error responses

| Status | Error | Description |
|--------|-------|-------------|
| 400 | `source is required and must be one of: user, agent, both` | Invalid or missing source |
| 400 | `category is required and must be one of: user_experience, agent_experience` | Invalid or missing category |
| 400 | `aspect must be one of: ...` | Aspect not valid for the given category |
| 400 | `rating must be an integer between 1 and 5` | Rating out of range |
| 400 | `At least one of rating or comment is required` | Neither rating nor comment provided |
| 400 | `comment must be 2000 characters or less` | Comment too long |
| 401 | `Unauthorized` | Missing or invalid token |
