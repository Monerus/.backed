from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from fastapi import Depends, status, HTTPException, APIRouter
from api.models import * 
from typing import List
from api.crud.auth_utils import *

router = APIRouter(prefix='/tasks', tags=["Tasks"])


@router.post("/create/", response_model=TasksResponse)
async def create_tasks(task_in: TasksCreate,
                       session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    task = Task(**task_in.model_dump())

    try:
        session.add(task)
        await session.commit()
        await session.refresh(task)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error: {e}")
    
    return task

@router.get('/get-tasks/', response_model=List[TasksResponse])
async def get_tasks(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    result = await session.execute(
        select(Task)
        .order_by(Task.reward))
    stmt = result.scalars().all()
    return stmt


@router.get("/get-tasks-me/", response_model=List[TasksResponse])
async def get_me_tasks(
    current_user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency)):

    query = (
        select(Task, UserTask)
        .join(UserTask, (UserTask.task_id == Task.id) & (UserTask.user_id == current_user.id))
        .order_by(Task.reward)
    )

    result = await session.execute(query)
    rows = result.all()

    tasks_with_progress = []

    for task_obj, user_task_obj in rows:
        tasks_with_progress.append({
            "id": task_obj.id,
            "title": task_obj.title,
            "reward": task_obj.reward,
            "step": task_obj.step, # Цель (например, 10)
            "current_step": user_task_obj.step if user_task_obj else 0, # Прогресс (например, 7)
        })
    
    return tasks_with_progress
