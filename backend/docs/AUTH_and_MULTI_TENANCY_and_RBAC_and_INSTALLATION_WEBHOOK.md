# Master Specification: Auth, Multi-Tenancy, RBAC & Installation Webhooks

## 1. Overview
This document serves as the master blueprint for the Trace.ai B2B architecture. It covers the complete user lifecycle from initial login and app installation to data isolation and role management.

---

## 2. The User Journey (Onboarding Flow)

### Step 1: Initial OAuth Login
- **Action:** User logs in via GitHub.
- **Backend:** 
    1. Verifies identity and creates/updates the `User` record.
    2. Fetches existing installations from GitHub.
    3. If `user.last_active_org_id` is null and no installations exist, the frontend prompts the user to **"Install Trace AI Security"**.

### Step 2: GitHub App Installation
- **Action:** User selects an Organization on GitHub and installs the app.
- **Background (Webhook):** GitHub sends an `installation:created` event. Our backend creates the `Organization` and `Repository` records.
- **Frontend Redirect:** GitHub redirects the user back to the app's setup page with `?installation_id=...`.

### Step 3: Zero-Touch Onboarding (Auto-Join)
- **Action:** The setup page detects the new installation.
- **Race Condition Handling:** 
    - The setup page should show a loading state (*"Finalizing your workspace..."*) and poll the backend until the `Organization` record is confirmed.
- **Backend:** 
    1. Automatically creates a row in `organization_members` for the user.
    2. Assigns the user the **ADMIN** role.
    3. Updates `user.last_active_org_id` to this new organization.
- **Result:** The user is instantly redirected to the dashboard for that specific organization.

---

## 3. Required Database Schema Changes (`app/models/core.py`)

We need to establish the B2B hierarchy.

```python
# 1. Organizations (The Tenant)
class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum("ORGANIZATION", "USER"), nullable=False)
    github_installation_id = Column(BigInteger, unique=True, index=True)

# 2. Memberships & Roles (The Bridge)
class OrganizationMember(Base):
    __tablename__ = 'organization_members'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    role = Column(Enum("ADMIN", "MEMBER", "VIEWER"), nullable=False)

# 3. User Updates (The Context)
class User(Base):
    __tablename__ = "users"
    # ... existing fields ...
    last_active_org_id = Column(Integer, ForeignKey('organizations.id'))
```

---

## 4. Webhook Implementation Logic (`app/api/routes/v1/webhooks.py`)

The `installation` event is the single source of truth for the workspace.

```python
@router.post("/github")
async def handle_webhook(x_github_event: str = Header(None)):
    if x_github_event == "installation":
        payload = await request.json()
        action = payload["action"]
        
        if action == "created":
            # 1. Create Organization in DB
            # 2. Call GitHub API to list all repositories
            # 3. Save repositories linked to the Organization ID
            
        elif action == "deleted":
            # Mark Organization as inactive
```

---

## 5. Authentication & Data Isolation Logic

### 5.1 Enriched JWT
The JWT must carry the "Active Context" to enforce isolation.
```json
{
  "sub": "johndoe",
  "org_id": 101,  // The current workspace
  "role": "ADMIN" // Permissions within this workspace
}
```

### 5.2 Scoped Queries (The "Wall")
Every query in the repository layer must join through the Repository to the Organization.

```python
# app/repositories/analytics_repo.py
async def get_feed(db, org_id):
    stmt = (
        select(Vulnerability)
        .join(PullRequest)
        .join(Repository)
        .where(Repository.organization_id == org_id) # Isolation enforced here
    )
    ...
```

---

## 6. Implementation Checklist (Code Changes)

1.  **Models:** Create `Organization` and `OrganizationMember` in `app/models/core.py`. Add `last_active_org_id` to `User`.
2.  **Migrations:** Run `alembic revision --autogenerate` and apply.
3.  **Auth Routing:** Update `app/api/routes/v1/auth.py` to:
    - Perform the Auto-Join logic.
    - Set the `last_active_org_id` on login if it's missing.
4.  **Dependencies:** Update `get_current_user` in `app/api/dependencies.py` to extract `org_id` and `role`.
5.  **Webhook Routing:** Update `app/api/routes/v1/webhooks.py` to handle `installation` events.
6.  **Analytics Scoping:** Refactor all methods in `app/repositories/analytics_repo.py` to accept an `organization_id` parameter.
7.  **Frontend Sync:** Ensure the React frontend handles the post-install redirect and calls the "Setup Sync" endpoint.
