from app.core.database import Database

async def get_db_pool():
    return Database.get_pool()