from fastapi import APIRouter, Depends, Query
from app.dependencies import get_db_pool
from app.schemas.repos import RepoBase, RepoListResponse
from app.crud.repos import get_top_100
import asyncpg

router = APIRouter()

@router.get("/top100", response_model=RepoListResponse)
async def top100(
    db_pool: asyncpg.Pool = Depends(get_db_pool),
    sort_by: str = Query(default="stars", description="Field to sort by"),
    order: str = Query(default="desc", description="Sort order: asc or desc")
):
    records = await get_top_100(db_pool, sort_by=sort_by, order=order)
    repos = [RepoBase(**dict(r)) for r in records]
    return RepoListResponse(repos=repos)
