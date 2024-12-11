from pydantic import BaseModel
from typing import List
from datetime import date

class ActivityItem(BaseModel):
    date: date
    commits: int
    authors: List[str]

class ActivityResponse(BaseModel):
    activity: List[ActivityItem]