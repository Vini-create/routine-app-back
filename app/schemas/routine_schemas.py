from pydantic import BaseModel, ConfigDict, Field, model_validator
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
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    style: str
    description: Optional[str] = None

class GoalCreate(BaseModel):
    title: str = Field(min_length = 2, max_length=60)
    description: Optional[str] = Field(default=None, max_length=200)
    category: Optional[GoalCategory] = Field(default=None)
    target_date: date

class GoalUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length = 2, max_length=60)
    description: Optional[str] = Field(default=None, max_length=200)
    category: Optional[GoalCategory] = None
    target_date: Optional[date] = None

class GoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: Optional[str] = None
    category: Optional[GoalCategory] = None
    target_date: Optional[date] = None


class RoutineItemCreate(BaseModel):
    schedule_type: ScheduleType
    start_at: datetime
    end_at: Optional[datetime] = None
    recurrence_rule: Optional[str] = Field(default=None, max_length=300)
    duration_minutes: int = Field(ge=1, le=1440) # 1 minute to 24 hours
    item_type: ItemType = Field(default=ItemType.TASK)
    description: Optional[str] = Field(default=None, max_length=200)
    title: str = Field(min_length=2, max_length=150)
    goal_id: Optional[UUID] = None

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
    description: Optional[str] = Field(default=None, max_length=200)
    title: Optional[str] = Field(default=None, min_length=2, max_length=150)
    goal_id: Optional[UUID] = None

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
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    schedule_type: ScheduleType
    start_at: datetime
    end_at: Optional[datetime] = None
    recurrence_rule: Optional[str] = None
    item_type: ItemType = Field(default=ItemType.TASK)
    description: Optional[str] = None
    title: str
    goal_id: Optional[UUID] = None
    duration_minutes: int
    
class HabitCreate(BaseModel):
    goal_id: UUID
    name: str = Field(min_length = 2, max_length=60)
    description: Optional[str] = Field(default=None, max_length=200)
    duration_minutes: int = Field(ge=1, le=1440) # 1 minute to 24 hours
    recurrence_rule: str = Field(max_length=300)
    start_date: date

    @model_validator(mode="after")
    def validate_recurrence(self):
        validate_recurrence_rule(self.recurrence_rule)
        return self

class HabitUpdate(BaseModel):
    goal_id: Optional[UUID] = None
    name: Optional[str] = Field(default=None, min_length = 2, max_length=60)
    description: Optional[str] = Field(default=None, max_length=200)
    duration_minutes: Optional[int] = Field(default=None, ge=1, le=1440) # 1 minute to 24 hours
    recurrence_rule: Optional[str] = Field(default=None, max_length=300)
    start_date: Optional[date] = None

    @model_validator(mode="after")
    def validate_recurrence(self):
        if self.recurrence_rule is not None:
            validate_recurrence_rule(self.recurrence_rule)
        return self

class HabitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    goal_id: Optional[UUID] = None
    name: str = Field(min_length = 2, max_length=60)    
    description: Optional[str] = None
    duration_minutes: int
    recurrence_rule: str
    start_date: date
    status: str

class HabitLogCreate(BaseModel):
    habit_id: UUID
    log_date: date
    status: ItemStatus
    
class HabitLogUpdate(BaseModel):
    habit_id: Optional[UUID] = None
    status: Optional[ItemStatus] = None
    
class HabitLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    routine_item_id: UUID
    log_date: date
    status: ItemStatus


class RoutineItemOccurrenceRead(BaseModel):
    item: RoutineItemRead
    occurrence_at: datetime
    occurrence_date: date
    status: ItemStatus
    log_id: Optional[UUID] = None


class HabitOccurrenceRead(BaseModel):
    habit: HabitRead
    goal: Optional[GoalRead] = None
    occurrence_date: date
    status: ItemStatus
    log_id: Optional[UUID] = None


class RoutineAgendaRead(BaseModel):
    start_date: date
    end_date: date
    routine_items: list[RoutineItemOccurrenceRead]
    habits: list[HabitOccurrenceRead]


class HabitDashboardOccurrenceRead(BaseModel):
    date: date
    status: ItemStatus
    log_id: Optional[UUID] = None


class HabitDashboardItemRead(BaseModel):
    habit: HabitRead
    goal: Optional[GoalRead] = None
    expected_count: int
    completed_count: int
    uncompleted_count: int
    pending_count: int
    consistency_percent: float
    consistency_level: str
    occurrences: list[HabitDashboardOccurrenceRead]


class HabitsDashboardRead(BaseModel):
    start_date: date
    end_date: date
    habits: list[HabitDashboardItemRead]


class GoalDashboardItemRead(BaseModel):
    goal: GoalRead
    expected_count: int
    completed_count: int
    uncompleted_count: int
    pending_count: int
    consistency_percent: float
    consistency_level: str
    habits: list[HabitDashboardItemRead]


class GoalsDashboardRead(BaseModel):
    start_date: date
    end_date: date
    goals: list[GoalDashboardItemRead]
    
