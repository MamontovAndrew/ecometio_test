from fastapi import APIRouter, Depends, Query
from datetime import date
from typing import Optional
from app.dependencies import get_db_pool
from app.schemas.activity import ActivityItem, ActivityResponse
from app.crud.activity import get_activity
from app.core.exceptions import NotFoundException
import asyncpg

router = APIRouter()

@router.get("/{owner}/{repo}/activity", response_model=ActivityResponse)
async def activity(
    owner: str,
    repo: str,
    since: date = Query(..., description="Start date YYYY-MM-DD"),
    until: date = Query(..., description="End date YYYY-MM-DD"),
    db_pool: asyncpg.Pool = Depends(get_db_pool)
):
    records = await get_activity(db_pool, owner, repo, since, until)
    if not records:
        return ActivityResponse(activity=[])
    activity_list = [ActivityItem(**dict(r)) for r in records]
    return ActivityResponse(activity=activity_list)
