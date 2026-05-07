# Technical Specification: Authentication & RBAC Flow

## 1. Introduction
This document provides a detailed technical walkthrough of the Authentication and Role-Based Access Control (RBAC) architecture for Trace.ai. This system is designed to support B2B multi-tenancy using GitHub App installations as the root of identity and isolation.

---

## 2. Conceptual Model

### 2.1 Identity vs. Tenant
*   **Identity (User):** A personal GitHub account (e.g., `@johndoe`). Identity is global.
*   **Tenant (Organization):** A workspace created from a GitHub App installation. A tenant owns data (repositories, vulnerabilities).
*   **Membership:** The link between an Identity and a Tenant, defined by a **Role**.

### 2.2 Roles & Permissions
| Role | Description | Permissions |
| :--- | :--- | :--- |
| **ADMIN** | Organization Owner | Manage members, change billing, delete organization, manage custom rules, view all analytics. |
| **MEMBER** | Standard Developer | View analytics, trigger manual scans, comment on vulnerabilities, manage rule overrides. |
| **VIEWER** | Stakeholder / Auditor | Read-only access to dashboards, reports, and vulnerability feeds. |

---

## 3. End-to-End Authentication Flow

### Step 1: GitHub OAuth Handshake
1.  User clicks **"Login with GitHub"** on the frontend.
2.  Frontend redirects to GitHub: `https://github.com/login/oauth/authorize`.
3.  User approves permissions.
4.  GitHub redirects back to the Backend: `/api/v1/auth/github/callback?code=...`.

### Step 2: Identity & Installation Discovery
1.  **Token Exchange:** Backend exchanges `code` for a GitHub `access_token`.
2.  **Fetch Profile:** Backend calls `GET https://api.github.com/user` to get the user's GitHub ID and login.
3.  **Fetch Installations:** Backend calls `GET https://api.github.com/user/installations`.
    *   This returns a list of organizations/accounts where the Trace.ai App is installed.
    *   *Example Result:* `[{id: 123, account: {login: "AcmeCorp"}}]`.

### Step 3: Database Synchronization
1.  **User Sync:** Find or create the `User` in the local DB.
2.  **Org Sync:** For each installation found in Step 2, find the corresponding `Organization` in the local DB (created via webhook).
3.  **Membership Sync:**
    *   If the user isn't a member of the Org in our DB, add them.
    *   If they are the first member, assign **ADMIN**. Otherwise, assign **VIEWER**.

### Step 4: JWT Issuance
The backend generates a JWT containing the user's identity and their **Current Organization Context**.

```json
{
  "sub": "johndoe",
  "user_id": 42,
  "org_id": 101,
  "role": "ADMIN",
  "iat": 1715090000,
  "exp": 1715176400
}
```

---

## 4. Authorization & RBAC Enforcement

### 4.1 Data Isolation (Row-Level Security)
Every database query in the repository layer **MUST** include the `org_id` from the JWT.

```python
# Secure Repository Pattern
async def get_recent_vulnerabilities(db, org_id, limit=10):
    stmt = (
        select(Vulnerability)
        .join(PullRequest)
        .join(Repository)
        .where(Repository.organization_id == org_id) # The "Wall"
        .order_by(Vulnerability.created_at.desc())
        .limit(limit)
    )
    return await db.execute(stmt)
```

### 4.2 Permission Enforcement (Middleware)
We use FastAPI dependencies to protect specific API actions based on the `role` inside the JWT.

```python
# Permission Dependency
def require_role(allowed_roles: list[str]):
    def decorator(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return decorator

# Protected Route
@router.delete("/repositories/{id}")
async def delete_repo(id: int, user = Depends(require_role(["ADMIN"]))):
    # Only ADMINs can reach this code
    ...
```

---

## 5. Lifecycle Events (Webhooks)

The `installation` webhook is the **source of truth** for tenant lifecycle management. It must be implemented to ensure the database stays in sync with GitHub.

### 5.1 Event: `installation`
This event is triggered when the app is installed, uninstalled, or its status changes.

#### Action: `created`
Triggered when a user installs the app on a personal or organization account.
- **Goal:** Create the "Tenant" (Organization) and initial repository metadata.
- **Implementation Logic:**
    1.  Extract `installation.id` and `installation.account.login` (Organization Name).
    2.  Check if an `Organization` with this `github_installation_id` already exists (to handle re-installs).
    3.  Create/Update the `Organization` record.
    4.  Iterate through `repositories` (if provided in payload) and save them, linking to the new `organization_id`.

#### Action: `deleted`
Triggered when the user uninstalls the app.
- **Goal:** Clean up or deactivate the tenant.
- **Implementation Logic:**
    1.  Find the `Organization` by `installation.id`.
    2.  Set `is_active = False` or delete organization-related data (depending on retention policy).
    3.  *Note:* This immediately blocks all users belonging to this Org from accessing analytics.

#### Action: `suspend` / `unsuspend`
- **Goal:** Temporarily block access.
- **Implementation Logic:** Update an `is_suspended` flag on the `Organization` table.

### 5.2 Implementation Blueprint (Python/FastAPI)

```python
# app/api/routes/v1/webhooks.py

if x_github_event == "installation":
    payload = await request.json()
    action = payload.get("action")
    installation_id = payload["installation"]["id"]
    org_name = payload["installation"]["account"]["login"]

    if action == "created":
        # 1. Upsert Organization
        org = await org_service.get_or_create_org(
            name=org_name, 
            installation_id=installation_id
        )
        # 2. Sync Repositories sent in the initial payload
        repos = payload.get("repositories", [])
        await repo_service.sync_initial_repos(org.id, repos)

    elif action == "deleted":
        await org_service.deactivate_org(installation_id)
```

### 5.3 Event: `installation_repositories`
Triggered when a user adds or removes specific repositories from an existing installation.
- **Action: `added`**: Create new `Repository` records linked to the `organization_id`.
- **Action: `removed`**: Mark repositories as inactive or delete them.

---
