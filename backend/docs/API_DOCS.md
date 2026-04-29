# Trace.ai Backend API Documentation

This document provides a comprehensive list of all available API endpoints in the Trace.ai backend.

## Base URL
The base URL for all API endpoints is:
`http://localhost:8000/api` (Development)

---

## General Endpoints

### 1. Root
**API Name:** Root  
**Description:** Returns basic information about the API, including name, description, and version.  
**URL:** `/`  
**Method:** `GET`  
**Request Type:** `None`  
**Sample Request:**  
`GET /`

**Response:**
```json
{
  "name": "trace-ai-backend",
  "description": "AI-powered security scanning for GitHub PRs",
  "version": "1.0.0"
}
```

### 2. Health Check
**API Name:** Health Check  
**Description:** Verifies that the API service is running and healthy.  
**URL:** `/api/health`  
**Method:** `GET`  
**Request Type:** `None`  
**Sample Request:**  
`GET /api/health`

**Response:**
```json
{
  "status": "Healthy",
  "service": "trace-ai-backend",
  "version": "1.0.0"
}
```

---

## Authentication Endpoints

### 3. GitHub OAuth Callback
**API Name:** GitHub OAuth Callback  
**Description:** Exchanges a GitHub OAuth code for a local JWT and user profile information.  
**URL:** `/api/v1/auth/github/callback`  
**Method:** `POST`  
**Request Type:** `application/json`  
**Sample Request:**
```json
{
  "code": "81d243bd2c585b0f4821"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "username": "octocat",
    "avatar_url": "https://github.com/images/error/octocat_happy.gif"
  }
}
```

---

## Analytics Endpoints
*Note: These endpoints require an `Authorization: Bearer <token>` header.*

### 4. Analytics Overview
**API Name:** Analytics Overview  
**Description:** Aggregates core security metrics for the dashboard.  
**URL:** `/api/v1/analytics/overview`  
**Method:** `GET`  
**Request Type:** `None`  
**Sample Request:**  
`GET /api/v1/analytics/overview`  
`Authorization: Bearer <token>`

**Response:**
```json
{
  "total_repositories": 12,
  "total_vulnerabilities": 45,
  "open_vulnerabilities": 10,
  "scanned_prs": 150,
  "critical_vulnerabilities": 2
}
```

### 5. Vulnerability Feed
**API Name:** Vulnerability Feed  
**Description:** Returns a list of the most recent security events and vulnerabilities.  
**URL:** `/api/v1/analytics/feed`  
**Method:** `GET`  
**Request Type:** `None`  
**Parameters:**
- `limit` (Query, Optional, Default: 10): Number of items to return.

**Sample Request:**  
`GET /api/v1/analytics/feed?limit=5`  
`Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 101,
    "title": "SQL Injection in Login Form",
    "severity": "CRITICAL",
    "status": "OPEN",
    "repository": "my-secure-app",
    "created_at": "2024-05-20T10:00:00Z"
  },
  ...
]
```

### 6. SOC2 PDF Report
**API Name:** SOC2 PDF Report  
**Description:** Generates and downloads a PDF audit report for a specific repository.  
**URL:** `/api/v1/analytics/report/soc2/pdf`  
**Method:** `GET`  
**Request Type:** `None`  
**Parameters:**
- `repository_id` (Query, Optional): The local database ID of the repository.
- `github_id` (Query, Optional): The GitHub ID of the repository.

*Note: One of either `repository_id` or `github_id` must be provided.*

**Sample Request:**  
`GET /api/v1/analytics/report/soc2/pdf?github_id=1296269`  
`Authorization: Bearer <token>`

**Response:**
- **Content-Type:** `application/pdf`
- **Body:** Binary PDF data.

---

## Webhook Endpoints

### 7. GitHub Webhook
**API Name:** GitHub Webhook  
**Description:** Handles incoming webhook events from GitHub, such as `pull_request` and `ping`.  
**URL:** `/api/v1/webhooks/github`  
**Method:** `POST`  
**Request Type:** `application/json`  
**Headers:**
- `X-Hub-Signature-256`: GitHub HMAC signature for security.
- `X-GitHub-Event`: The type of event (e.g., `pull_request`, `ping`).

**Sample Request (Pull Request):**
```json
{
  "action": "opened",
  "number": 1,
  "pull_request": {
    "url": "https://api.github.com/repos/owner/repo/pulls/1",
    "id": 123456,
    "title": "Fix security vulnerability",
    "user": {
      "login": "octocat",
      "id": 1,
      "avatar_url": "https://github.com/images/error/octocat_happy.gif"
    },
    "diff_url": "https://github.com/owner/repo/pull/1.diff",
    "head": { ... },
    "base": { ... }
  },
  "repository": {
    "id": 1296269,
    "full_name": "owner/repo",
    "private": false,
    "owner": { ... }
  },
  "sender": { ... },
  "installation": { "id": 123 }
}
```

**Response:**
```json
{
  "status": "accepted",
  "message": "PR event received"
}
```

---

## GitHub Endpoints
*Note: These endpoints require an `Authorization: Bearer <token>` header.*

### 8. List Repositories
**API Name:** List Repositories  
**Description:** Fetches all repositories accessible to the specified GitHub App installation.  
**URL:** `/api/v1/github/repositories`  
**Method:** `GET`  
**Request Type:** `None`  
**Parameters:**
- `installation_id` (Query, Required): The GitHub App installation ID.

**Sample Request:**  
`GET /api/v1/github/repositories?installation_id=123`  
`Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1296269,
    "name": "hello-world",
    "full_name": "octocat/hello-world",
    "private": false,
    "owner": {
      "login": "octocat",
      "id": 1,
      "avatar_url": "https://github.com/images/error/octocat_happy.gif"
    },
    "html_url": "https://github.com/octocat/hello-world",
    "description": "This your first repo!",
    ...
  }
]
```

---

## Custom Rule Endpoints
*Note: These endpoints require an `Authorization: Bearer <token>` header.*

### 9. List Rules by Repository
**API Name:** List Rules by Repository  
**Description:** Fetches all custom security rules for a specific repository.  
**URL:** `/api/v1/rules/repository/{repository_id}`  
**Method:** `GET`  
**Request Type:** `None`  
**Sample Request:**  
`GET /api/v1/rules/repository/1`  
`Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "repository_id": 1,
    "rule_text": "Never use MD5 hashing, enforce SHA-256.",
    "is_active": true,
    "created_at": "2024-05-20T10:00:00Z"
  }
]
```

### 10. Create Custom Rule
**API Name:** Create Custom Rule  
**Description:** Adds a new custom security rule to a repository.  
**URL:** `/api/v1/rules/`  
**Method:** `POST`  
**Request Type:** `application/json`  
**Sample Request:**
```json
{
  "repository_id": 1,
  "rule_text": "Enforce strict typing in all TypeScript files.",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 2,
  "repository_id": 1,
  "rule_text": "Enforce strict typing in all TypeScript files.",
  "is_active": true,
  "created_at": "2024-05-20T11:00:00Z"
}
```

### 11. Get Custom Rule
**API Name:** Get Custom Rule  
**Description:** Fetches details of a specific custom security rule.  
**URL:** `/api/v1/rules/{rule_id}`  
**Method:** `GET`  
**Request Type:** `None`  
**Sample Request:**  
`GET /api/v1/rules/1`  
`Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "repository_id": 1,
  "rule_text": "Never use MD5 hashing, enforce SHA-256.",
  "is_active": true,
  "created_at": "2024-05-20T10:00:00Z"
}
```

### 12. Update Custom Rule
**API Name:** Update Custom Rule  
**Description:** Updates the text or active status of an existing custom security rule.  
**URL:** `/api/v1/rules/{rule_id}`  
**Method:** `PATCH`  
**Request Type:** `application/json`  
**Sample Request:**
```json
{
  "rule_text": "Use SHA-512 instead of MD5.",
  "is_active": false
}
```

**Response:**
```json
{
  "id": 1,
  "repository_id": 1,
  "rule_text": "Use SHA-512 instead of MD5.",
  "is_active": false,
  "created_at": "2024-05-20T10:00:00Z"
}
```

### 13. Delete Custom Rule
**API Name:** Delete Custom Rule  
**Description:** Permanently removes a custom security rule.  
**URL:** `/api/v1/rules/{rule_id}`  
**Method:** `DELETE`  
**Request Type:** `None`  
**Sample Request:**  
`DELETE /api/v1/rules/1`  
`Authorization: Bearer <token>`

**Response:**
`204 No Content`

