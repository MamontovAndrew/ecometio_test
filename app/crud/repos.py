import asyncpg
from typing import List

async def get_top_100(pool: asyncpg.Pool, sort_by: str = "stars", order: str = "desc") -> List[asyncpg.Record]:
    valid_sort_fields = ["stars", "position_cur", "position_prev", "watchers", "forks", "open_issues", "language"]
    if sort_by not in valid_sort_fields:
        sort_by = "stars"
    order = order.lower()
    if order not in ["asc", "desc"]:
        order = "desc"

    query = f"""
    SELECT repo, owner, position_cur, position_prev, stars, watchers, forks, open_issues, language
    FROM top100
    ORDER BY {sort_by} {order}
    LIMIT 100
    """
    return await pool.fetch(query)