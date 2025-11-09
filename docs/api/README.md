# API Documentation

## Authentication

### Register a new user

**POST** `/api/auth/register`

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false
}
```

### Login

**POST** `/api/auth/login`

```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Refresh Token

**POST** `/api/auth/refresh`

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Agents

### List all agents

**GET** `/api/agents/`

Query Parameters:
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "name": "Data Validator",
    "description": "Validates incoming data",
    "agent_type": "validator",
    "status": "active",
    "config": {},
    "version": "1.0.0",
    "is_plugin": false
  }
]
```

### Create an agent

**POST** `/api/agents/`

```json
{
  "name": "Custom Analyzer",
  "description": "Analyzes data patterns",
  "agent_type": "analyzer",
  "config": {
    "threshold": 0.8
  },
  "version": "1.0.0"
}
```

### Get agent by ID

**GET** `/api/agents/{agent_id}`

### Update an agent

**PUT** `/api/agents/{agent_id}`

```json
{
  "name": "Updated Agent Name",
  "status": "active",
  "config": {
    "new_param": "value"
  }
}
```

### Delete an agent

**DELETE** `/api/agents/{agent_id}`

### Activate an agent

**POST** `/api/agents/{agent_id}/activate`

### Deactivate an agent

**POST** `/api/agents/{agent_id}/deactivate`

### List available agent types

**GET** `/api/agents/registry/list`

**Response:**
```json
{
  "agents": ["validator", "analyzer", "enricher", "transformer"]
}
```

## Pipelines

### List all pipelines

**GET** `/api/pipelines/`

### Create a pipeline

**POST** `/api/pipelines/`

```json
{
  "name": "Data Processing Pipeline",
  "description": "Validates, analyzes, and enriches data",
  "config": {},
  "steps": [
    {
      "agent_id": 1,
      "order": 1,
      "config": {}
    },
    {
      "agent_id": 2,
      "order": 2,
      "config": {}
    }
  ]
}
```

### Execute a pipeline

**POST** `/api/pipelines/{pipeline_id}/execute`

```json
{
  "input_data": {
    "field1": "value1",
    "field2": "value2"
  }
}
```

**Response:**
```json
{
  "execution_id": 123,
  "status": "pending",
  "input_data": {...},
  "output_data": null,
  "started_at": "2024-01-01T12:00:00Z"
}
```

## Audit Logs

### List audit logs

**GET** `/api/audit-logs/`

Query Parameters:
- `skip` (int): Number of records to skip
- `limit` (int): Maximum number of records to return
- `action` (str): Filter by action type
- `resource_type` (str): Filter by resource type
- `user_id` (int): Filter by user ID

## Admin

### List users

**GET** `/api/admin/users/`

### Create role

**POST** `/api/admin/roles/`

```json
{
  "name": "data_analyst",
  "description": "Can view and analyze data"
}
```

### Assign role to user

**POST** `/api/admin/users/{user_id}/roles`

```json
{
  "role_id": 1
}
```

### Add permission to role

**POST** `/api/admin/roles/{role_id}/permissions`

```json
{
  "resource": "agent",
  "action": "read"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- Anonymous: 100 requests per hour
- Authenticated: 1000 requests per hour

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets (Unix timestamp)
