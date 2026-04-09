import argparse
import subprocess
from pathlib import Path

def run_cmd(cmd: list[str]) -> int:
    result = subprocess.run(cmd, check=False)
    return result.returncode


def stamp_head() -> None:
    exit_code = run_cmd(["alembic", "stamp", "head"])
    if exit_code != 0:
        raise SystemExit(exit_code)


def upgrade_head() -> None:
    exit_code = run_cmd(["alembic", "upgrade", "head"])
    if exit_code != 0:
        raise SystemExit(exit_code)


def autogenerate_revision(message: str) -> None:
    exit_code = run_cmd(["alembic", "revision", "--autogenerate", "-m", message])
    if exit_code != 0:
        raise SystemExit(exit_code)


def ensure_repo_root() -> None:
    repo_backend_root = Path(__file__).resolve().parents[1]
    if Path.cwd() != repo_backend_root:
        # Alembic relies on local alembic.ini and import paths.
        # Running from backend root keeps behavior consistent.
        raise SystemExit(
            f"Run this script from backend root: {repo_backend_root}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync database tables/fields using Alembic migrations."
    )
    parser.add_argument(
        "--autogenerate",
        action="store_true",
        help="Create a new Alembic migration from model changes before upgrade.",
    )
    parser.add_argument(
        "--message",
        default="Auto schema update",
        help="Migration message used when --autogenerate is set.",
    )
    parser.add_argument(
        "--stamp-existing",
        action="store_true",
        help=(
            "Stamp current DB schema to head before upgrade. "
            "Useful for existing databases not yet tracked by Alembic."
        ),
    )
    args = parser.parse_args()

    ensure_repo_root()

    if args.autogenerate:
        print("Generating migration from current model changes...")
        autogenerate_revision(args.message)

    if args.stamp_existing:
        print("Stamping existing schema with Alembic head...")
        stamp_head()

    print("Applying migrations to database...")
    upgrade_head()
    print("Database schema is up to date.")


if __name__ == "__main__":
    main()
