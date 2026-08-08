from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, not_
from sqlalchemy.orm import selectinload
from fastapi import Depends, status, HTTPException, APIRouter
from api.models import * 
from api.crud.auth_utils import *
from api.crud.task_utils import *

router = APIRouter(prefix='/tasks', tags=["Tasks"])


# Для админа
@router.post("/create/", response_model=TasksResponse)
async def create_task(
    task_in: TasksBase,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    task = Task(**task_in.model_dump())

    try:
        session.add(task)
        await session.commit()
        await session.refresh(task)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error: {e}"
        )

    return task


# Для админа
@router.get('/get-tasks/', response_model=None)
async def get_tasks(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    result = await session.execute(
        select(Task)
        .order_by(Task.reward))
    stmt = result.scalars().all()
    return stmt



@router.get("/get-me-tasks/", response_model=list[UserTaskResponse])
async def get_me_tasks(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    query = (
        select(Task, UserTask)
        .outerjoin(
            UserTask, 
            (UserTask.task_id == Task.id) & 
            (UserTask.user_id == current_user.id)
        )
        .where(
            UserTask.reward_claimed == False
        )
    )
    result = await session.execute(query)
    rows = result.all()

    response = []

    for task, user_task in rows:
        
        if user_task is None:
            user_task = UserTask(
                user_id=current_user.id,
                task_id=task.id
            )
            session.add(user_task)  
            await session.flush()

        reset_task_if_needed(user_task)
        user_task.step = current_user.score

        if not user_task.completed and user_task.step >= task.last_step:
            user_task.completed = True

        response.append(UserTaskResponse(
            id=user_task.id,
            task_id=task.id,
            title=task.title,
            step=user_task.step,
            last_step=task.last_step,
            completed=user_task.completed,
            reward=task.reward,
            reward_claimed=user_task.reward_claimed
        ))

    await session.commit()
    return response


@router.post("/claim-reward/{task_id}/")
async def claim_reward(
    task_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user: User = Depends(get_current_user)
):
    
    query = (
        select(UserTask)
        .options(selectinload(UserTask.task))
        .where(
            UserTask.task_id == task_id,
            UserTask.user_id == current_user.id
        )
        .with_for_update()
    )

    result = await session.execute(query)
    user_task = result.scalar_one_or_none()

    if not user_task:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )

    reset_task_if_needed(user_task)

    if not user_task.completed:
        raise HTTPException(
            status_code=400,
            detail="Задача еще не выполнена"
        )

    if user_task.reward_claimed:
        raise HTTPException(
            status_code=400,
            detail="Награда уже получена"
        )

    task_result = await session.execute(
        select(Task).where(Task.id == task_id)
    )

    task = task_result.scalar_one()

    reward_amount = task.reward

    current_user.gold += reward_amount
    user_task.reward_claimed = True

    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(500, "Ошибка базы данных")

    return {
        "status": "ok",
        "reward_received": reward_amount,
        "current_gold": current_user.gold
    }
    



    
