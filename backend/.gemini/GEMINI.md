# Trace AI Backend: Development Mandates

You are an expert Backend Engineer for **Trace AI**. You follow a strict Service-Repository pattern with FastAPI and SQLAlchemy 2.0 (Async).

## 🏗️ Architectural Layers

### 1. Database & Models (`app/models/`)
- **Naming:** Use PascalCase for class names and snake_case for table names.
- **Base:** Inherit from `DeclarativeBase` (see `app/core/database.py`).
- **Async:** Always use `async_sessionmaker` and `create_async_engine`.

### 2. Repositories (`app/repositories/`)
- **Mandate:** ALL database access MUST go through a repository. NO direct DB calls in routes or services.
- **Pattern:** Inherit from `BaseRepo` in `base_repo.py`.
- **Methods:** Use type-hinted methods for all CRUD operations.

### 3. Services (`app/services/`)
- **Mandate:** ALL business logic (e.g., AI scanning, calculations, 3rd-party integrations) MUST live here.
- **Dependency:** Services should be injected into Routes.

### 4. API & Routing (`app/api/routes/`)
- **Mandate:** Routes should ONLY handle HTTP concerns: request parsing, service calls, and response status codes.
- **Naming:** Use plural nouns for endpoints.
- **Response Schemas:** Every route MUST have a `response_model`.

### 5. Schemas (`app/schemas/`)
- **Pydantic v2:** Use Pydantic v2 exclusively.
- **Split:** Create separate schemas for `Create`, `Update`, and `Read` (Response).

## 🛠️ Coding Standards

### Error Handling
- Use custom exception classes in a `app/core/exceptions.py` (create if missing).
- Use FastAPI's `HTTPException` for client-facing errors.
- Never let raw DB errors bubble up to the client.

### Logging
- Use standard Python `logging`.
- Log all major events (scans started, webhooks received, errors).

### Code Quality
- **Ruff:** All code must pass `task lint` and `task format`.
- **Typing:** Strict type hinting for all function signatures.

## 🚀 Efficiency & Bug Fixing
- **Reproduce First:** Before fixing a bug, create a reproduction script or test case.
- **DRY:** Extract common logic into `app/utils/` (e.g., `diff_parser.py`).
- **Migrations:** Any model change REQUIRES an Alembic migration.
