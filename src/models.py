from datetime import datetime as dt
from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    id: int
    account_name: str
    private_key: Optional[str]


class Quiz(BaseModel):
    id: int
    name: Optional[str]
    price: float
    due: dt
    is_finished: bool


class UserScore(BaseModel):
    id: int
    score: int
    quiz_id: int
    user_id: int
    shard: Optional[str]
