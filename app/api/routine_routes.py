from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.dependencies import get_current_verified_user
from app.api.rate_limit import limiter
from app.db.db import get_session
from app.models.auth import User
from app.schemas.auth_schemas import MessageResponse
from app.schemas.routine_schemas import (
    GoalCreate,
    GoalRead,
    GoalUpdate,
    GoalsDashboardRead,
    HabitCreate,
    HabitDashboardItemRead,
    HabitLogCreate,
    HabitLogRead,
    HabitsDashboardRead,
    HabitRead,
    HabitUpdate,
    RoutineAgendaRead,
    RoutineItemCreate,
    RoutineItemLogCreate,
    RoutineItemLogRead,
    RoutineItemRead,
    RoutineItemUpdate,
)
from app.services import routine_service

routine_router = APIRouter(prefix="/routine", tags=["routine"])


def _bad_request(error: ValueError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(error),
    )


@routine_router.get("/agenda", response_model=RoutineAgendaRead)
@limiter.limit("60/minute")
async def get_agenda(
    request: Request,
    start_date: date,
    end_date: date,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Returns routine items and habit occurrences for the calendar/timeline screen.
    try:
        return await routine_service.get_routine_agenda(
            session,
            current_user.id,
            start_date,
            end_date,
        )
    except ValueError as error:
        raise _bad_request(error)


@routine_router.post("/items", response_model=RoutineItemRead)
@limiter.limit("30/minute")
async def create_routine_item(
    request: Request,
    payload: RoutineItemCreate,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Creates a task/event/reminder block that can be single or recurring.
    try:
        return await routine_service.create_routine_item(session, current_user.id, payload)
    except ValueError as error:
        raise _bad_request(error)


@routine_router.get("/items", response_model=list[RoutineItemRead])
@limiter.limit("60/minute")
async def list_routine_items(
    request: Request,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Lists the saved routine item definitions for management screens.
    return await routine_service.list_routine_items(session, current_user.id)


@routine_router.get("/items/{item_id}", response_model=RoutineItemRead)
@limiter.limit("60/minute")
async def get_routine_item(
    request: Request,
    item_id: UUID,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Returns one routine item owned by the current user.
    try:
        return await routine_service.get_routine_item(session, current_user.id, item_id)
    except ValueError as error:
        raise _bad_request(error)


@routine_router.patch("/items/{item_id}", response_model=RoutineItemRead)
@limiter.limit("30/minute")
async def update_routine_item(
    request: Request,
    item_id: UUID,
    payload: RoutineItemUpdate,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Updates a routine item without allowing cross-user access.
    try:
        return await routine_service.update_routine_item(
            session,
            current_user.id,
            item_id,
            payload,
        )
    except ValueError as error:
        raise _bad_request(error)


@routine_router.delete("/items/{item_id}", response_model=MessageResponse)
@limiter.limit("20/minute")
async def delete_routine_item(
    request: Request,
    item_id: UUID,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Permanently deletes a routine item after frontend confirmation.
    try:
        await routine_service.delete_routine_item(session, current_user.id, item_id)
        return {"message": "Routine item deleted successfully"}
    except ValueError as error:
        raise _bad_request(error)


@routine_router.post("/items/logs", response_model=RoutineItemLogRead)
@limiter.limit("60/minute")
async def save_routine_item_log(
    request: Request,
    payload: RoutineItemLogCreate,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Marks a routine item occurrence as completed/uncompleted within the allowed window.
    try:
        return await routine_service.save_routine_item_log(
            session,
            current_user.id,
            payload,
        )
    except ValueError as error:
        raise _bad_request(error)


@routine_router.get("/habits/dashboard", response_model=HabitsDashboardRead)
@limiter.limit("60/minute")
async def get_habits_dashboard(
    request: Request,
    start_date: date,
    end_date: date,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Returns all habits with goal labels and consistency for the selected period.
    try:
        return await routine_service.get_habits_dashboard(
            session,
            current_user.id,
            start_date,
            end_date,
        )
    except ValueError as error:
        raise _bad_request(error)


@routine_router.post("/habits", response_model=HabitRead)
@limiter.limit("30/minute")
async def create_habit(
    request: Request,
    payload: HabitCreate,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Creates a recurring habit, optionally attached to a goal.
    try:
        return await routine_service.create_habit(session, current_user.id, payload)
    except ValueError as error:
        raise _bad_request(error)


@routine_router.get("/habits", response_model=list[HabitRead])
@limiter.limit("60/minute")
async def list_habits(
    request: Request,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Lists habit definitions for simple management screens.
    return await routine_service.list_habits(session, current_user.id)


@routine_router.get("/habits/{habit_id}", response_model=HabitRead)
@limiter.limit("60/minute")
async def get_habit(
    request: Request,
    habit_id: UUID,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Returns one habit owned by the current user.
    try:
        return await routine_service.get_habit(session, current_user.id, habit_id)
    except ValueError as error:
        raise _bad_request(error)


@routine_router.patch("/habits/{habit_id}", response_model=HabitRead)
@limiter.limit("30/minute")
async def update_habit(
    request: Request,
    habit_id: UUID,
    payload: HabitUpdate,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Updates a habit definition and validates goal ownership.
    try:
        return await routine_service.update_habit(
            session,
            current_user.id,
            habit_id,
            payload,
        )
    except ValueError as error:
        raise _bad_request(error)


@routine_router.delete("/habits/{habit_id}", response_model=MessageResponse)
@limiter.limit("20/minute")
async def delete_habit(
    request: Request,
    habit_id: UUID,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Permanently deletes a habit after frontend confirmation.
    try:
        await routine_service.delete_habit(session, current_user.id, habit_id)
        return {"message": "Habit deleted successfully"}
    except ValueError as error:
        raise _bad_request(error)


@routine_router.post("/habits/logs", response_model=HabitLogRead)
@limiter.limit("60/minute")
async def save_habit_log(
    request: Request,
    payload: HabitLogCreate,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Marks a habit occurrence as completed/uncompleted within the allowed window.
    try:
        return await routine_service.save_habit_log(session, current_user.id, payload)
    except ValueError as error:
        raise _bad_request(error)


@routine_router.get("/goals/dashboard", response_model=GoalsDashboardRead)
@limiter.limit("60/minute")
async def get_goals_dashboard(
    request: Request,
    end_date: date,
    start_date: date | None = None,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Returns goals with their habits and consistency for monthly or all-time analysis.
    try:
        return await routine_service.get_goals_dashboard(
            session,
            current_user.id,
            end_date,
            start_date,
        )
    except ValueError as error:
        raise _bad_request(error)


@routine_router.post("/goals", response_model=GoalRead)
@limiter.limit("30/minute")
async def create_goal(
    request: Request,
    payload: GoalCreate,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Creates a goal that can group habits and routine items.
    try:
        return await routine_service.create_goal(session, current_user.id, payload)
    except ValueError as error:
        raise _bad_request(error)


@routine_router.get("/goals", response_model=list[GoalRead])
@limiter.limit("60/minute")
async def list_goals(
    request: Request,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Lists all goals owned by the current user.
    return await routine_service.list_goals(session, current_user.id)


@routine_router.get("/goals/{goal_id}", response_model=GoalRead)
@limiter.limit("60/minute")
async def get_goal(
    request: Request,
    goal_id: UUID,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Returns one goal owned by the current user.
    try:
        return await routine_service.get_goal(session, current_user.id, goal_id)
    except ValueError as error:
        raise _bad_request(error)


@routine_router.get("/goals/{goal_id}/habits", response_model=list[HabitDashboardItemRead])
@limiter.limit("60/minute")
async def get_goal_habits(
    request: Request,
    goal_id: UUID,
    start_date: date,
    end_date: date,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Returns habits attached to one goal with consistency for the selected period.
    try:
        return await routine_service.get_goal_habits_dashboard(
            session,
            current_user.id,
            goal_id,
            start_date,
            end_date,
        )
    except ValueError as error:
        raise _bad_request(error)


@routine_router.patch("/goals/{goal_id}", response_model=GoalRead)
@limiter.limit("30/minute")
async def update_goal(
    request: Request,
    goal_id: UUID,
    payload: GoalUpdate,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Updates a goal owned by the current user.
    try:
        return await routine_service.update_goal(
            session,
            current_user.id,
            goal_id,
            payload,
        )
    except ValueError as error:
        raise _bad_request(error)


@routine_router.delete("/goals/{goal_id}", response_model=MessageResponse)
@limiter.limit("20/minute")
async def delete_goal(
    request: Request,
    goal_id: UUID,
    session=Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Permanently deletes a goal after frontend confirmation.
    try:
        await routine_service.delete_goal(session, current_user.id, goal_id)
        return {"message": "Goal deleted successfully"}
    except ValueError as error:
        raise _bad_request(error)
