import asyncio
from sqlalchemy import text
from app.core.database import engine

async def check():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        print(f"Tables: {[r[0] for r in res]}")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check())
