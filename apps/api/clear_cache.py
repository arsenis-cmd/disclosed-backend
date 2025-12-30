"""
Clear Detection table cache to force fresh detections
"""
import asyncio
import asyncpg
import os

async def clear_cache():
    # Get DATABASE_URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return

    print(f"Connecting to database...")
    conn = await asyncpg.connect(database_url)

    try:
        # Delete all cached detections
        result = await conn.execute('DELETE FROM "Detection" WHERE "textHash" IS NOT NULL')
        print(f"Cleared detection cache: {result}")
        print("✓ Cache cleared successfully!")
    finally:
        await conn.close()
        print("Database connection closed")

if __name__ == "__main__":
    asyncio.run(clear_cache())
