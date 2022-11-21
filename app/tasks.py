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

    if not task.user_phrase.base_phrase.pronunciation:
        download_pronunciation_task(task.user_phrase.base_phrase.id)
        task.refresh_from_db()

    send_message(
        task.user.telegram_chat_id,
        task.user_phrase.base_phrase.value,
        task.user_phrase.base_phrase.pronunciation
    )

    task.user.user_schedule.send_on_schedule = False
    task.user.user_schedule.save()


@app.task
def download_pronunciation_task(phrase_id):
    phrase = Phrase.objects.get(id=phrase_id)
    if phrase.pronunciation:
        return

    try:
        text = phrase.value.replace('*', '').replace(' ', '%20')
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
