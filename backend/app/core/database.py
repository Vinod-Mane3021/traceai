from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Create the async engine
engine = create_async_engine(
    settings.DATABASE_URL, 
    # echo=True, # Set to True if you want to see all SQL queries printed in the terminal

    # --- Serverless DB Optimizations (Crucial for Neon) ---
    pool_pre_ping=True,  # Tests the connection before executing a query to prevent disconnect errors
    pool_size=5,         # Maximum number of permanent connections to keep open
    max_overflow=10,     # How many extra temporary connections to open during traffic spikes
)

# ---------------------------------------------------------
# Session Maker Setup
# ---------------------------------------------------------

# async_sessionmaker acts as a factory for creating new database sessions.
# This is what gets yielded inside your get_db() dependency.
async_session_maker = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession,
    expire_on_commit=False,  # Prevents SQLAlchemy from fetching the object again after a commit
    autoflush=False,
    autocommit=False
)