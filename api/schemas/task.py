from datetime import datetime
from pydantic import BaseModel


class TaskCreate(BaseModel):
    creator_id: int
    content: str
    creation_date: datetime