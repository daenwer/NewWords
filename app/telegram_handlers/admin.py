import uuid

from aiogram import types
from aiogram.utils.exceptions import BotBlocked
from django.utils import timezone

from app.management.commands.bot import bot, dp
from app.telegram_handlers.sync_with_async import _get_user, _save
from app.management.commands.bot import bot

from django.contrib.auth import login


@dp.message_handler(commands=['admin'])
async def admin_command(message: types.Message):
    user = await _get_user(message.chat.id)
    if user:
        user.token = uuid.uuid4()
        user.date_create_token = timezone.now()
        await _save(user)
        text_message = (
            # TODO: ссылка на урл с токеном сначала дописать)))
            f'http://127.0.0.1:8000/login/{user.token}/'
        )
    else:
        text_message = (
            'Register please!)'
        )
    try:
        await bot.send_message(message.chat.id, text_message)
    except BotBlocked:
        if user:
            user.is_active = False
            await _save(user)



# from django.contrib.sessions.models import Session
# from django.contrib.auth.models import User
#
# session_key = '8cae76c505f15432b48c8292a7dd0e54'
#
# session = Session.objects.get(session_key=session_key)
# uid = session.get_decoded().get('_auth_user_id')
# user = User.objects.get(pk=uid)
#
# print user.username, user.get_full_name(), user.email