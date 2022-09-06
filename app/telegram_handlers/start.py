from aiogram import types
from aiogram.utils.exceptions import BotBlocked

from app.management.commands.bot import bot, dp
from app.telegram_handlers.sync_async import _get_or_create_user, \
    _get_user, _save


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await _get_or_create_user(message)
    text_message = (
        'This bot can help you ...\n'
        '/help - for information'
    )
    try:
        await bot.send_message(message.chat.id, text_message)
    except BotBlocked:
        user = await _get_user(message.chat.id)
        user.is_active = False
        await _save(user)
