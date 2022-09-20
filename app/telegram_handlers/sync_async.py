import datetime
from datetime import timedelta

from asgiref.sync import sync_to_async

from app.models import User
from app.models.base import Phrase, UserPhrase, UserSchedule, RepeatSchedule
from app.tasks import download_pronunciation_task


@sync_to_async
def _save(user):
    user.save()


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
def _get_phrase(phrase):
    if record := Phrase.objects.filter(value=phrase):
        return record.first()
    return None


@sync_to_async
def _get_user_phrase(record, user):
    if user_record := UserPhrase.objects.filter(base_phrase=record, user=user):
        return user_record.first()
    return None


@sync_to_async
def _create_phrase(phrase, user):
    new_phrase = Phrase.objects.create(value=phrase, user=user)
    # download_pronunciation_task.delay(new_phrase.id)
    # download_pronunciation_task(new_phrase.id)
    return new_phrase


@sync_to_async
def _create_user_phrase(base_phrase, user):
    return UserPhrase.objects.create(base_phrase=base_phrase, user=user)


@sync_to_async
def _create_repeat_schedule(user, user_phrase):
    next_repeat = (
        datetime.datetime.now() +
        datetime.timedelta(seconds=user.user_schedule.repetition_0)
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
