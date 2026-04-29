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
**Method:** `GET`  
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
- `repository_id` (Query, Required): The ID of the repository to generate the report for.

**Sample Request:**  
`GET /api/v1/analytics/report/soc2/pdf?repository_id=1`  
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
