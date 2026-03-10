from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class EventCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=500)
    start_time: datetime
    end_time: datetime


class EventResponse(BaseModel):
    event_id: str
    user_id: str
    event_date: str
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    created_at: datetime



class PaginatedEventResponse(BaseModel):
    items: list[EventResponse]
    next_key: Optional[str] = None