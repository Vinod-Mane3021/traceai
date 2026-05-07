# B2B Multi-Tenancy & RBAC Implementation Guide

## 1. Overview
This document outlines the architectural changes required to transition the application to a robust B2B multi-tenant model with Role-Based Access Control (RBAC). The goal is to ensure strict data isolation and granular permission management.

## 2. Defining the "Tenant" (Organization vs. Personal)

The application recognizes two types of tenants based on the GitHub `account.type` field provided in webhooks and API responses. Both types are stored in the `organizations` table but behave differently regarding membership.

### 2.1. Organization Accounts (`type: "Organization"`)
- **Nature:** Represents a business, team, or open-source org.
- **Membership:** Designed for multi-user access. Users gain access if they are members of the GitHub organization and have the Trace.ai app authorized.
- **RBAC:** Admins can invite/manage other members of the org within Trace.ai.

### 2.2. Personal Accounts (`type: "User"`)
- **Nature:** Represents an individual's personal repositories.
- **Membership:** Typically restricted to the owner of the account.
- **RBAC:** The owner is the permanent ADMIN. Other users usually do not have access to a personal tenant unless explicitly invited for collaboration.

## 3. Database Schema Changes

### 3.1. New Tables

#### `organizations`
Represents a customer/tenant.
- `id`: Integer (PK)
- `name`: String (e.g., "Acme Corp" or "johndoe")
- `type`: Enum ("ORGANIZATION", "USER") - *Added to distinguish account types*
- `github_installation_id`: BigInteger (Unique, Index)
- `created_at`: DateTime
- `updated_at`: DateTime

#### `organization_members`
Intersection table for multi-org support and RBAC.
- `user_id`: Integer (FK -> users.id, PK)
- `organization_id`: Integer (FK -> organizations.id, PK)
- `role`: Enum ("ADMIN", "MEMBER", "VIEWER")
- `joined_at`: DateTime

### 3.2. Modified Tables

#### `repositories`
- Add `organization_id`: Integer (FK -> organizations.id, Index).
- All webhooks must link incoming repositories to their parent Organization via the `installation_id`.

#### `users`
- (Optional) Remove `installation_id`.
- Add `last_active_org_id`: Integer (ForeignKey -> `organizations.id`). This acts as a pointer to the user's most recently used workspace.
- **Model Recommendation:** Rename the relationship from `organization` to `active_organization` to explicitly state this is a context pointer, not the user's only membership.

---

## 4. Authentication & Onboarding Journey

### 4.1. Account Discovery & Sync
1.  **OAuth Login:** User logs in via GitHub.
2.  **Fetch Installations:** Backend calls `GET /user/installations`.
3.  **Tenant Processing:** For each installation:
    - Extract `account.login` (Name) and `account.type` (Type).
    - Upsert the `Organization` with the correct `type`.
    - Link the `User` to the `Organization` in `organization_members` (Auto-Join Strategy).
    - If `type == "User"`, the user is automatically granted `ADMIN` of their own personal org.
    - If `type == "Organization"`, role is determined by GitHub Org permissions (e.g., GitHub Org Owners become Trace.ai Admins).

### 4.2. Active Org Dashboard Flow
To reduce friction, the application guides the user directly to their active workspace:
1.  **Login:** User authenticates.
2.  **Logic:**
    - **IF** `user.last_active_org_id` exists:
        - Redirect to `/dashboard/{org_id}`.
    - **ELSE (First-time user or no active context):** Check GitHub API for any authorized installations.
        - **IF Found:**
            - Pick the first installation, sync the membership, set as `last_active_org_id`.
            - Redirect to `/dashboard/{org_id}`.
        - **IF None:** 
            - **IMMEDIATELY redirect** to the **"Install Trace AI Security"** onboarding page. 
            - This page provides a clear call-to-action to install the app on GitHub.

### 4.3. Handling the Installation "Race Condition"
When a user installs the app, GitHub triggers a Webhook (`created`) and a Redirect (`setup_url`) simultaneously.
- **Problem:** The user might arrive at the Setup page before the Webhook has finished creating the Organization in the DB.
- **Solution:** 
    - The Setup page should show a loading state: *"Finalizing your workspace..."*.
    - It should poll the backend (e.g., `GET /api/v1/organizations/check/{installation_id}`) until the record is found.
    - Once found, the backend sets the `last_active_org_id` and the frontend redirects to the Dashboard.

### 4.4. JWT Payload
The local JWT includes the `organization_id` to establish the "Active Context".
```json
{
  "org_id": 101,
  "role": "ADMIN",
  "org_type": "ORGANIZATION"
}
```

---

## 5. Webhook Lifecycle Management

### 5.1. Handling `installation` Event
- **Action: `created`**: 
    1. Create/Update the `Organization` using `installation.id` and `installation.account.type`.
    2. Immediately fetch all repositories for this installation via GitHub API.
    3. Save repositories to the DB, setting their `organization_id`.
- **Action: `deleted`**:
    1. Find the `Organization` by `installation.id`.
    2. Mark as `inactive`.
- **Action: `suspend`**: Mark the Org as `suspended`.

---

## 6. Data Isolation (The Fix)

### 6.1. Scoped Repository Queries
All analytics queries must join through `Repository` and filter by `organization_id`.

**Example SQL:**
```sql
SELECT v.* 
FROM vulnerabilities v
JOIN pull_requests pr ON v.pull_request_id = pr.id
JOIN repositories r ON pr.repository_id = r.id
WHERE r.organization_id = :current_org_id;
```

---

## 7. Role-Based Access Control (RBAC)

### 7.1. Defined Roles
- **ADMIN:** Full access to settings, custom rules, and members.
- **MEMBER:** Can view analytics and trigger scans.
- **VIEWER:** Read-only access.

---

## 8. Migration Path
1.  **Step 1:** Create the `organizations` table.
2.  **Step 2:** Populate `organizations` from existing data, using `github_id` to infer `type` if possible, or defaulting to `USER`.
3.  **Step 3:** Add `organization_id` to `repositories`.
4.  **Step 4:** Update Auth and Repository logic.
