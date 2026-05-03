from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, not_
from sqlalchemy.orm import selectinload
from fastapi import Depends, status, HTTPException, APIRouter
from api.models import * 
from typing import List
from api.crud.auth_utils import *

router = APIRouter(prefix='/tasks', tags=["Tasks"])


# Для админа
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


# Для админа
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
            step = 0
            completed = False
        else:
            step = user_task.step
            completed = user_task.completed
        # 3. Логика проверки прогресса (например, по score пользователя)
        # Обновляем текущий шаг, если он привязан к score
        user_task.step = current_user.score 

        if not user_task.completed and user_task.step >= task.last_step:
            user_task.completed = True

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
            "completed": user_task.completed,
            "reward": task.reward
        })

    return response


@router.post("/claim-reward/{task_id}/")
async def claim_reward(task_id: int,
                       session: AsyncSession = Depends(db_helper.scoped_session_dependency),
                       current_user: Users = Depends(get_current_user)):
    
    query = (
        select(UserTask)
        .options(selectinload(UserTask.task))
        .where(
            UserTask.task_id == task_id,
            UserTask.user_id == current_user.id
        )
    )

    result = await session.execute(query)
    user_task = result.scalar_one_or_none()

    if not user_task:
       raise HTTPException(status_code=404, detail="Task not found")

    if not user_task.completed:
        raise HTTPException(status_code=400, detail="Task not completed")
    
    if user_task.reward_claimed:
        raise HTTPException(status_code=400, detail="Already claimed")

    
    reward = user_task.task.reward

    current_user.gold += reward
    user_task.reward_claimed = True

    await session.commit()

    return {
        "status": "ok",
        "gold": current_user.gold
    }
    



    
