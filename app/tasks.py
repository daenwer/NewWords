import datetime
import os.path
import urllib.request

from NewWords.celery import app
from NewWords.settings import BASE_DIR
from app.models.base import RepeatSchedule, Phrase
from app.telegram_handlers.send_message import send_message


@app.task
def create_new_celery_task(task_id):
    task = RepeatSchedule.objects.filter(id=task_id).first()

    if not task.user.is_active:
        return

    send_message(
        task.user.telegram_chat_id,
        task.user_phrase.base_phrase.value,
        task.user_phrase.base_phrase.pronunciation
    )

    if not task.user_phrase.base_phrase.pronunciation:
        download_pronunciation_task.delay(task.user_phrase.base_phrase.id)

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


@app.task
def download_pronunciation_task(phrase_id):
    phrase = Phrase.objects.get(id=phrase_id)
    if phrase.pronunciation:
        return

    try:
        text = phrase.value.replace(' ', '%20')
        # USA - 0; UK - 1
        url = f'http://dict.youdao.com/dictvoice?type=0&audio={text}'
        file_path = os.path.join(
            BASE_DIR, 'app', 'static', 'audio', f'{phrase.id}.mp3'
        )
        urllib.request.urlretrieve(url, filename=file_path)
        phrase.pronunciation = f'{phrase.id}.mp3'
        phrase.save()
    except:
        pass
