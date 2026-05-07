# B2B Multi-Tenancy & RBAC Implementation Guide

## 1. Overview
This document outlines the architectural changes required to transition the application to a robust B2B multi-tenant model with Role-Based Access Control (RBAC). The goal is to ensure strict data isolation and granular permission management.

## 2. Database Schema Changes

### 2.1. New Tables

#### `organizations`
Represents a customer/tenant (e.g., a GitHub Organization or a specific User's personal installation).
- `id`: Integer (PK)
- `name`: String (e.g., "Acme Corp")
- `github_installation_id`: BigInteger (Unique, Index)
- `created_at`: DateTime
- `updated_at`: DateTime

#### `organization_members`
Intersection table for multi-org support and RBAC.
- `user_id`: Integer (FK -> users.id, PK)
- `organization_id`: Integer (FK -> organizations.id, PK)
- `role`: Enum ("ADMIN", "MEMBER", "VIEWER")
- `joined_at`: DateTime

### 2.2. Modified Tables

#### `repositories`
- Add `organization_id`: Integer (FK -> organizations.id, Index).
- All webhooks must link incoming repositories to their parent Organization via the `installation_id`.

#### `users`
- (Optional) Remove `installation_id` if users can belong to multiple organizations via `organization_members`.

---

## 3. Authentication & Authorization

### 3.1. OAuth Flow Updates
1.  **Installation Discovery:** After GitHub OAuth, fetch `/user/installations`.
2.  **Organization Sync:**
    - For each `installation_id`, find or create the `Organization` record.
    - Add the user to `organization_members` if not already present.
3.  **JWT Payload:** The local JWT should include:
    - `organization_id`: The ID of the currently active organization context.
    - `role`: The user's role within that organization.

### 3.2. Scoped Dependencies
Update `get_current_user` to return an object containing the user's ID, the active `organization_id`, and their `role`.

---

## 4. Webhook Lifecycle Management

The `installation` webhook is the "Glue" that manages the Tenant lifecycle. It must be implemented to ensure the system reacts to GitHub App events.

### 4.1. Handling `installation` Event
- **Action: `created`**: 
    1. Create/Update the `Organization` using `installation.id`.
    2. Immediately fetch all repositories for this installation via GitHub API.
    3. Save repositories to the DB, setting their `organization_id`.
- **Action: `deleted`**:
    1. Find the `Organization` by `installation.id`.
    2. Mark as `inactive`. This immediately revokes access for all members in the next JWT validation.
- **Action: `suspend`**: Mark the Org as `suspended`.

### 4.2. Handling `installation_repositories` Event
- **Action: `added`**: Add new `Repository` rows linked to the `organization_id`.
- **Action: `removed`**: Delete or deactivate `Repository` rows.

---

## 5. Data Isolation (The Fix)

### 5.1. Scoped Repository Queries
All analytics queries must join through `Repository` and filter by `organization_id`.

**Before (Vulnerable):**
```sql
SELECT * FROM vulnerabilities ORDER BY created_at DESC LIMIT 10;
```

**After (Secure):**
```sql
SELECT v.* 
FROM vulnerabilities v
JOIN pull_requests pr ON v.pull_request_id = pr.id
JOIN repositories r ON pr.repository_id = r.id
WHERE r.organization_id = :current_org_id
ORDER BY v.created_at DESC 
LIMIT 10;
```

---

## 6. Role-Based Access Control (RBAC)

### 6.1. Defined Roles
- **ADMIN:** Full access to organization settings, custom rules, and member management.
- **MEMBER:** Can view analytics, trigger scans, and manage vulnerabilities.
- **VIEWER:** Read-only access to analytics and reports.

### 6.2. Implementation via Middleware
Create a `check_permission` dependency to enforce roles on specific routes:

```python
@router.post("/rules")
async def create_rule(
    current_user = Depends(require_role(["ADMIN"]))
):
    ...
```

---

## 7. Migration Path
1.  **Step 1:** Create the `organizations` table.
2.  **Step 2:** Populate `organizations` from existing unique `installation_id` values in the `users` and `repositories` tables.
3.  **Step 3:** Add `organization_id` column to `repositories` and populate via `installation_id` mapping.
4.  **Step 4:** Deploy code updates for Auth and Analytics queries.
5.  **Step 5:** Enforce NOT NULL constraints on `organization_id` columns.
