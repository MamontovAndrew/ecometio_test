import asyncpg
from typing import List
from datetime import date

async def get_activity(
    pool: asyncpg.Pool, owner: str, repo: str, since: date, until: date
) -> List[asyncpg.Record]:
    query = """
    SELECT date, commits, authors
    FROM activity
    WHERE owner = $1 AND repo = $2 AND date >= $3 AND date <= $4
    ORDER BY date ASC
    """
    return await pool.fetch(query, owner, repo, since, until)
