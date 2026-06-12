from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import date, datetime
from enum import Enum
from uuid import UUID

from app.services.recurrence import validate_recurrence_rule

###Para cada recurso:
###- Create
###- Update
###- Read

# ENUMS

class GoalCategory(str, Enum):
    HEALTH = "health"
    PRODUCTIVITY = "productivity"
    LEARNING = "learning"
    FITNESS = "fitness"
    MENTAL_WELLNESS = "mental_wellness"
    OTHER = "other"

class ItemStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    UNCOMPLETED = "uncompleted"

class ItemType(str, Enum):
    HABIT = "habit"
    TASK = "task"
    EVENT = "event"
    REMINDER = "reminder" 

class GoalStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    WITHOUT_SUCCESS = "without_success"

class ScheduleType(str, Enum):
    SINGLE = "single"
    RECURRING = "recurring"


#SCHEMAS

class CoachProfileCreate(BaseModel):
    name: str = Field(min_length = 2, max_length=40)
    style: str = Field(min_length = 2, max_length=80)
    description: Optional[str] = Field(default=None, max_length=200)

class CoachProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length = 2, max_length=40)
    style: Optional[str] = Field(default=None, min_length = 2, max_length=80)
    description: Optional[str] = Field(default=None, max_length=200)

class CoachProfileRead(BaseModel):
    id: UUID
    name: str
    style: str
    description: Optional[str] = None

class GoalCreate(BaseModel):
    title: str = Field(min_length = 2, max_length=60)
    description: Optional[str] = Field(default=None, max_length=200)
    category: Optional[GoalCategory] = Field(default=None)

class GoalUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length = 2, max_length=60)
    description: Optional[str] = Field(default=None, max_length=200)
    category: Optional[GoalCategory] = None

class GoalRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    category: Optional[GoalCategory] = None


class RoutineItemCreate(BaseModel):
    schedule_type: ScheduleType
    start_at: datetime
    end_at: Optional[datetime] = None
    recurrence_rule: Optional[str] = Field(default=None, max_length=300)
    duration_minutes: int = Field(ge=1, le=1440) # 1 minute to 24 hours
    item_type: ItemType = Field(default=ItemType.TASK)

    @model_validator(mode="after")
    def validate_schedule(self):
        if self.end_at is not None and self.end_at <= self.start_at:
            raise ValueError("end_at must be greater than start_at")
        
        if self.schedule_type == ScheduleType.RECURRING and not self.recurrence_rule:
            raise ValueError("recurrence_rule is required for recurring items")

        if self.schedule_type == ScheduleType.SINGLE and self.recurrence_rule:
            raise ValueError("recurrence_rule is only allowed for recurring items")
        
        if self.schedule_type == ScheduleType.RECURRING and self.recurrence_rule:
            validate_recurrence_rule(self.recurrence_rule)

        return self
    
class RoutineItemUpdate(BaseModel):
    schedule_type: Optional[ScheduleType] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    recurrence_rule: Optional[str] = Field(default=None, max_length=300)
    duration_minutes: Optional[int] = Field(default=None, ge=1, le=1440) # 1 minute to 24 hours
    item_type: Optional[ItemType] = None

    @model_validator(mode="after")
    def validate_schedule(self):
        if self.end_at is not None and self.start_at is not None and self.end_at <= self.start_at:
            raise ValueError("end_at must be greater than start_at")
        
        if self.schedule_type == ScheduleType.RECURRING and not self.recurrence_rule:
            raise ValueError("recurrence_rule is required for recurring items")

        if self.schedule_type == ScheduleType.SINGLE and self.recurrence_rule:
            raise ValueError("recurrence_rule is only allowed for recurring items")
        
        if self.schedule_type == ScheduleType.RECURRING and self.recurrence_rule:
            validate_recurrence_rule(self.recurrence_rule)

        return self
    
class RoutineItemRead(BaseModel):
    id: UUID
    schedule_type: ScheduleType
    start_at: datetime
    end_at: Optional[datetime] = None
    recurrence_rule: Optional[str] = None
    item_type: ItemType = Field(default=ItemType.TASK)

class HabitCreate(BaseModel):
    goal_id: Optional[UUID] = None
    name: str = Field(min_length = 2, max_length=60)
    description: Optional[str] = Field(default=None, max_length=200)
    duration_minutes: int = Field(ge=1, le=1440) # 1 minute to 24 hours
    recurrence_rule: str = Field(max_length=300)
    start_date: date

class HabitUpdate(BaseModel):
    goal_id: Optional[UUID] = None
    name: Optional[str] = Field(default=None, min_length = 2, max_length=60)
    description: Optional[str] = Field(default=None, max_length=200)
    duration_minutes: Optional[int] = Field(default=None, ge=1, le=1440) # 1 minute to 24 hours
    recurrence_rule: Optional[str] = Field(default=None, max_length=300)
    start_date: Optional[date] = None

class HabitRead(BaseModel):
    id: UUID
    goal_id: Optional[UUID] = None
    name: str = Field(min_length = 2, max_length=60)    
    description: Optional[str] = None

class HabitLogCreate(BaseModel):
    habit_id: UUID
    log_date: date
    status: ItemStatus
    
class HabitLogUpdate(BaseModel):
    habit_id: Optional[UUID] = None
    status: Optional[ItemStatus] = None
    
class HabitLogRead(BaseModel):
    id: UUID
    habit_id: UUID
    log_date: date
    status: ItemStatus
    
#faltam os schemas de RoutineItemLog e colocar item type no RoutineItemCreate e RoutineItemUpdate

class RoutineItemLogCreate(BaseModel):
    routine_item_id: UUID
    log_date: date
    status: ItemStatus
    
class RoutineItemLogUpdate(BaseModel):
    routine_item_id: Optional[UUID] = None
    status: Optional[ItemStatus] = None

class RoutineItemLogRead(BaseModel):
    id: UUID
    routine_item_id: UUID
    log_date: date
    status: ItemStatus
    