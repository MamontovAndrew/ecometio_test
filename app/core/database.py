import asyncpg
import asyncio
from app.core.config import settings

class Database:
    _pool = None

    @classmethod
    async def connect(cls):
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                min_size=1,
                max_size=10
            )

    @classmethod
    async def close(cls):
        if cls._pool:
            await cls._pool.close()

    @classmethod
    def get_pool(cls):
        return cls._pool
    
    @classmethod
    async def check_tables_exist(cls):
        async with cls._pool.acquire() as conn:
            top100_exists = await conn.fetchval("SELECT to_regclass('public.top100')")
            activity_exists = await conn.fetchval("SELECT to_regclass('public.activity')")

            if not top100_exists:
                raise RuntimeError("Таблица 'top100' не существует. Пожалуйста, создайте её в БД перед запуском.")
            
            if not activity_exists:
                raise RuntimeError("Таблица 'activity' не существует. Пожалуйста, создайте её в БД перед запуском.")
