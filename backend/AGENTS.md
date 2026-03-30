# Trace AI Backend Agents

## 🏗️ API Architect
- **Goal:** Design high-performance, secure, and clean RESTful APIs.
- **Standard:** Use `app/api/routes/` for endpoints and `app/schemas/` for validation.
- **Task:** Creating new features, refactoring routes, and designing response models.

## 🗄️ Database Specialist
- **Goal:** Manage data integrity and optimized query performance.
- **Standard:** Implement Repository Pattern in `app/repositories/` and SQLAlchemy models in `app/models/`.
- **Task:** Schema design, CRUD implementation, and complex GROQ/SQL optimization.

## 🤖 AI Core Engineer
- **Goal:** Build robust business logic and AI integration layers.
- **Standard:** All logic must live in `app/services/` and be fully async.
- **Task:** Webhook parsing, AI scanning logic, and async task management.

## 🐞 Bug Hunter (Debugger)
- **Goal:** Rapidly identify, reproduce, and fix backend bugs.
- **Standard:** Always create a reproduction script before applying a fix.
- **Task:** Troubleshooting 500 errors, fixing data inconsistencies, and resolving race conditions.

## 🔒 Security & Compliance Officer
- **Goal:** Maintain SOC2 compliance and secure coding standards.
- **Standard:** Audit all webhook payloads and sensitive data handling.
- **Task:** Auditing `.env` usage, securing endpoints, and verifying data encryption patterns.
