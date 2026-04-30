from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, not_
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


@router.get('/get-tasks/', response_model=None)
async def get_tasks(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    result = await session.execute(
        select(Task)
        .order_by(Task.reward))
    stmt = result.scalars().all()
    return stmt


@router.get("/get-tasks-me/", response_model=List[UserTaskResponse])
async def get_me_tasks(
    current_user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    # 1. Получаем все задачи и прогресс текущего юзера
    query = (
        select(Task, UserTask)
        .outerjoin(
            UserTask, 
            (UserTask.task_id == Task.id) & 
            (UserTask.user_id == current_user.id)
        )
    )

    result = await session.execute(query)
    rows = result.all()

    response = []

    for task, user_task in rows:
        # 2. Если записи о прогрессе нет — создаем её (Lazy Creation)
        if user_task is None:
            user_task = UserTask(
                user_id=current_user.id,
                task_id=task.id,
                step=0,
                completed=False,
                reward_claimed=False
            )
            session.add(user_task)

        # 3. Логика проверки прогресса (например, по score пользователя)
        # Обновляем текущий шаг, если он привязан к score
        user_task.step = current_user.score 

        if not user_task.completed and user_task.step >= task.last_step:
            user_task.completed = True

        # 4. Награда
        if user_task.completed and not user_task.reward_claimed:
            current_user.gold += task.reward
            user_task.reward_claimed = True

        # Чтобы выполненные задания пропадали.
        if user_task.completed:
            continue

        # 5. Собираем данные для ответа (ВАЖНО: append должен быть ВНУТРИ цикла)
        response.append({
            "id": user_task.id,       # ID записи прогресса
            "task_id": task.id,       # ID самой задачи
            "user_id": current_user.id,
            "title": task.title,
            "step": user_task.step,
            "last_step": task.last_step,
            "completed": user_task.completed
        })

    await session.commit()
    return response