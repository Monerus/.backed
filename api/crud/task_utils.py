from datetime import date
from core.models import *

def reset_task_if_needed(user_task: UserTask):
    today = date.today()
    task_type = user_task.task.task_type

    if task_type == TaskType.PERMANENT:
        return

    # DAILY
    if task_type == TaskType.DAILY:
        if user_task.last_reset_date != today:
            _reset(user_task, today)


    # WEEKLY
    elif task_type == TaskType.WEEKLY:
        if user_task.last_reset_date.isocalendar()[1] != today.isocalendar()[1]:
            _reset(user_task, today)


def _reset(user_task: UserTask, today: date):
    user_task.step = 0
    user_task.completed = False
    user_task.reward_claimed = False
    user_task.last_reset_date = today