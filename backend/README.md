# Trace AI Backend
Automated SOC2 & Security Compliance Engine.

## Project Structure
```text
.
├── app/
│   ├── api/                # API routes and dependencies
│   │   ├── routes/         # Individual endpoint modules
│   │   └── dependencies.py # FastAPI dependencies (e.g., get_db)
│   ├── core/               # Core configuration and database setup
│   │   ├── config.py       # Pydantic settings
│   │   └── database.py     # SQLAlchemy async engine & session
│   ├── models/             # SQLAlchemy database models
│   ├── repositories/       # Data access layer (Repository pattern)
│   ├── schemas/            # Pydantic validation schemas
│   ├── services/           # Business logic and AI services
│   ├── utils/              # Helper utilities
│   ├── main.py             # FastAPI application entry point
│   └── __init__.py
├── .gemini/                # Gemini CLI configuration
│   ├── GEMINI.md           # Project mandates
│   └── settings.json       # CLI settings
├── AGENTS.md               # Specialized AI agent definitions
├── dev.py                  # Development server script
├── pyproject.toml          # Taskipy and project configuration
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (local only)
```

## Getting Started
### 1. Setup Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Development Server
```bash
task dev
```

## Commands
- `task dev`: Start development server with reload.
- `task lint`: Run ruff linting.
- `task format`: Run ruff formatting.

---
## Stop the containers AND destroy the attached volumes (-v)
docker compose down -v

## update requirements.txt file
pip freeze > requirements.txt



