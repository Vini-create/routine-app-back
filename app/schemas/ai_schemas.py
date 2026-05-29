from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime
from uuid import UUID
from datetime import date


#db

class ChatMessageCreate(BaseModel):
    role: str
    content: str
    content_type: str = "text"

class ChatMessageRead(BaseModel):
    id: UUID
    role: str
    content: str
    content_type: str
    created_at: datetime

class FeedbackRead(BaseModel):
    id: UUID    
    content: dict[str, Any]
    created_at: datetime
    goal_id: Optional[UUID] = None

#requests 

class FeedbackRequest(BaseModel):
    goal_id: UUID
    coach_profile_id: UUID
    period_start: date
    period_end: Optional[date] = None

class CoachChatRequest(BaseModel):
    coach_profile_id: UUID
    user_message: str