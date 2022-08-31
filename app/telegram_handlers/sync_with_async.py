from asgiref.sync import sync_to_async

from app.models import User
from app.models.base import Phrase, UserPhrase, UserSchedule

from django.contrib.auth import login


# from app.tasks import setup_periodic_tasks


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
    return User.objects.filter(
        telegram_chat_id=chat_id, is_active=True
    ).first()


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
    return Phrase.objects.create(value=phrase, user=user)


@sync_to_async
def _create_user_phrase(base_phrase, user):
    return UserPhrase.objects.create(base_phrase=base_phrase, user=user)


async def add_new_phrase(message):
    chat_id = message.from_user.id
    text = message.message.text
    user = await _get_user(chat_id)

    phrase = await _get_phrase(text)
    if not phrase:
        if len(text) > 511:
            return
        phrase = await _create_phrase(text, user)

    user_phrase = await _get_user_phrase(phrase, user)
    if not user_phrase:
        user_phrase = await _create_user_phrase(phrase, user)
        # # TODO: добавить в задачи для выполнения через первый промежуток
        # UserPhrase.save()
    else:
        print('повтор!!!!!!!!!!!!!!!!!!')
        # TODO: дописать логику при повторении, скинуть еще кнопки и уточнить
