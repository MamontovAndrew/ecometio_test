from pydantic import BaseModel
from typing import Optional

class RepoBase(BaseModel):
    repo: str
    owner: str
    position_cur: int
    position_prev: Optional[int]
    stars: int
    watchers: int
    forks: int
    open_issues: int
    language: Optional[str]

class RepoListResponse(BaseModel):
    repos: list[RepoBase]