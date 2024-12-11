from fastapi import APIRouter
from .endpoints import repos, activity

api_router = APIRouter()
api_router.include_router(repos.router, prefix="/repos", tags=["repos"])
api_router.include_router(activity.router, prefix="/repos", tags=["activity"])