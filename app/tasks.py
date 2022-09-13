import datetime
from NewWords.celery import app
from app.models.base import RepeatSchedule
from app.telegram_handlers.send_message import send_message


@app.task
def prepare_new_celery_tasks():
    current_datetime = datetime.datetime.now()
    current_tasks = RepeatSchedule.objects.filter(
        is_active=True, next_repeat__lte=current_datetime
    )
    for task in current_tasks:
        # create_new_celery_task.delay(task.id)
        create_new_celery_task(task.id)


@app.task
def create_new_celery_task(task_id):
    task = RepeatSchedule.objects.filter(id=task_id).first()

    if not task.user.is_active:
        return

    send_message(task.user.telegram_chat_id, task.user_phrase.base_phrase.value)

    try:
        next_step_repeat = (
            task.user_phrase.repeat_schedule['schedule'].index(False)
        )
    except ValueError:
        next_step_repeat = None

    if not next_step_repeat:
        task.is_active = False
        task.save()
        return

    # TODO: может удалять вместо остановки?
    task.user_phrase.repeat_schedule['schedule'][next_step_repeat] = True
    task.user_phrase.save()

    next_time_interval = task.user.user_schedule.__getattribute__(
        f'repetition_{next_step_repeat}'
    )
    current_datetime = datetime.datetime.now()
    next_datetime_repeat = (
        current_datetime + datetime.timedelta(seconds=next_time_interval)
    )
    lately_today = datetime.datetime(
        year=current_datetime.year,
        month=current_datetime.month,
        day=current_datetime.day,
        hour=task.user.user_schedule.finish_time.hour,
        minute=task.user.user_schedule.finish_time.minute
    )

    if next_datetime_repeat <= lately_today:
        hour = next_datetime_repeat.hour
        minute = next_datetime_repeat.minute
    else:
        if next_datetime_repeat.date() == lately_today.date():
            next_datetime_repeat += datetime.timedelta(days=1)
        hour = task.user.user_schedule.start_time.hour
        minute = task.user.user_schedule.start_time.minute

    user_next_datetime_repeat = datetime.datetime(
        year=next_datetime_repeat.year,
        month=next_datetime_repeat.month,
        day=next_datetime_repeat.day,
        hour=hour,
        minute=minute,
    )
    task.next_repeat = user_next_datetime_repeat
    task.save()
