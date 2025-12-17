from typing import AsyncGenerator
import asyncpg
from config import get_settings

settings = get_settings()


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=5,
            max_size=20,
        )

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def get_connection(self) -> AsyncGenerator:
        async with self.pool.acquire() as connection:
            yield connection


db = Database()


async def get_db():
    async for connection in db.get_connection():
        yield connection
