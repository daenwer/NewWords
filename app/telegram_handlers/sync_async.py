import datetime
import random
from datetime import timedelta

from asgiref.sync import sync_to_async

from app.models import User
from app.models.base import Phrase, UserPhrase, UserSchedule, RepeatSchedule
from app.tasks import create_new_celery_task, download_pronunciation_task


@sync_to_async
def _save(obj):
    obj.save()


@sync_to_async
def _get_or_create_user(message):
    user = User.objects.filter(telegram_chat_id=message.chat.id)
    if user:
        user = user[0]
        if not user.is_active:
            user.is_active = True
            user.save()
            user.refresh_from_db()
    else:
        user_schedule = UserSchedule.objects.create()
        user = User.objects.create(
            telegram_chat_id=message.chat.id,
            username=message.chat.username,
            first_name=message.chat.first_name,
            last_name=message.chat.last_name,
            user_schedule=user_schedule,
            is_staff=True,
        )
    return user


@sync_to_async
def _get_user(chat_id):
    if record := User.objects.filter(telegram_chat_id=chat_id, is_active=True):
        return record.first()
    return None


@sync_to_async
def _send_next_phrase(chat_id):
    current_datetime = datetime.datetime.now()
    user = User.objects.filter(telegram_chat_id=chat_id, is_active=True).first()
    next_tasks = RepeatSchedule.objects.filter(
        user=user, is_active=True, next_repeat__lte=current_datetime
    ).order_by('next_repeat').first()
    if next_tasks:
        create_new_celery_task(next_tasks.id)
    else:
        user.user_schedule.send_on_schedule = True
        user.user_schedule.save()


@sync_to_async
def _set_next_repeat_current_task(message):
    user = User.objects.filter(
        telegram_chat_id=message.chat.id, is_active=True
    ).first()
    phrase = message.caption
    caption_entities = message.values.get('caption_entities')
    caption_entities.reverse()
    if caption_entities:
        for step in caption_entities:
            new_phrase = (
                phrase[:(step.offset + step.length)] + '*' +
                phrase[(step.offset + step.length):]
            )
            new_phrase = (
                new_phrase[:step.offset] + '*' + new_phrase[step.offset:]
            )
            phrase = new_phrase
    user_phrase = UserPhrase.objects.filter(
        user=user, base_phrase__value=phrase
    ).first()
    task = RepeatSchedule.objects.filter(
        user_phrase=user_phrase, user=user
    ).first()

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

    start_hour = task.user.user_schedule.start_time.hour
    start_minute = task.user.user_schedule.start_time.minute

    if next_datetime_repeat <= lately_today:
        if next_datetime_repeat.hour <= task.user.user_schedule.start_time.hour:
            start = start_hour + start_minute / 60
            finish = start + 2
        else:
            if next_datetime_repeat.hour - start_hour > 1:
                start = (
                    next_datetime_repeat.hour - 1 +
                    next_datetime_repeat.minute / 60
                )
                finish = start + 1
            else:
                start = start_hour + start_minute / 60
                finish = start + 1
    else:
        if next_datetime_repeat.date() == lately_today.date():
            next_datetime_repeat += datetime.timedelta(days=1)
        if next_step_repeat == 1:
            start = start_hour + start_minute / 60
            finish = start + 2
        else:
            finish_hour = task.user.user_schedule.finish_time.hour - 1
            finish_minute = task.user.user_schedule.finish_time.minute
            start = start_hour + start_minute / 60
            finish = finish_hour + finish_minute / 60

    alarm = random.uniform(start, finish)
    hour = int(alarm)
    minute = int((alarm - hour) * 60)

    user_next_datetime_repeat = datetime.datetime(
        year=next_datetime_repeat.year,
        month=next_datetime_repeat.month,
        day=next_datetime_repeat.day,
        hour=hour,
        minute=minute,
    )
    task.next_repeat = user_next_datetime_repeat
    task.save()


@sync_to_async
def _get_phrase(phrase):
    if record := Phrase.objects.filter(value=phrase):
        return record.first()
    return None


@sync_to_async
def _download_pronunciation_task(*args):
    download_pronunciation_task(*args)


@sync_to_async
def _get_user_phrase(record, user):
    if user_record := UserPhrase.objects.filter(base_phrase=record, user=user):
        return user_record.first()
    return None


@sync_to_async
def _create_phrase(phrase, user):
    new_phrase = Phrase.objects.create(value=phrase, user=user)
    return new_phrase


@sync_to_async
def _create_user_phrase(base_phrase, user):
    return UserPhrase.objects.create(base_phrase=base_phrase, user=user)


@sync_to_async
def _create_repeat_schedule(user, user_phrase):
    next_repeat = (
        datetime.datetime.now() +
        datetime.timedelta(
            seconds=user.user_schedule.repetition_0 + random.randint(-600, 600)
        )
    )
    repeat_schedule = (True, *user_phrase.repeat_schedule['schedule'][1:])
    user_phrase.repeat_schedule['schedule'] = repeat_schedule
    user_phrase.save()
    RepeatSchedule.objects.create(
        user=user, user_phrase=user_phrase, next_repeat=next_repeat
    )


async def add_new_phrase(message):
    chat_id = message.from_user.id
    user = await _get_user(chat_id)

    text = message.message.text.strip()
    while '  ' in text:
        text = text.replace('  ', ' ')
    phrase = await _get_phrase(text)
    if not phrase:
        if len(text) > 511:
            return
        phrase = await _create_phrase(text, user)

    user_phrase = await _get_user_phrase(phrase, user)
    if not user_phrase:
        user_phrase = await _create_user_phrase(phrase, user)
        await _create_repeat_schedule(user=user, user_phrase=user_phrase)


@sync_to_async
def update_phrase(callback):
    user = User.objects.filter(
        telegram_chat_id=callback.message.chat.id, is_active=True
    ).first()
    old_phrase = callback.message.text.split('\n')[1].strip()
    new_phrase = callback.message.text.split('\n')[3].strip()
    old_app_phrase = Phrase.objects.filter(value=old_phrase).first()
    new_app_phrase = Phrase.objects.filter(value=new_phrase).first()
    user_phrase = UserPhrase.objects.filter(base_phrase=old_app_phrase).first()
    is_used = UserPhrase.objects.exclude(user=user).filter(
        base_phrase_id=old_app_phrase.id
    ).exists()

    if not is_used:
        if not new_app_phrase:
            old_app_phrase.value = new_phrase
            old_app_phrase.pronunciation = None
            old_app_phrase.save()
            # download_pronunciation_task(old_app_phrase.id)
        else:
            user_phrase.base_phrase = new_app_phrase
            user_phrase.save()
    else:
        phrase = Phrase.objects.create(value=new_phrase, user=user)
        user_phrase.base_phrase = phrase
        user_phrase.save()
        # download_pronunciation_task.delay(phrase.id)
        # download_pronunciation_task(phrase.id)
