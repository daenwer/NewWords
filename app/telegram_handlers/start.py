from aiogram import types
from aiogram.utils.exceptions import BotBlocked
from aiogram.utils.markdown import text

from app.management.commands.bot import bot, dp
from app.telegram_handlers.sync_async import _get_or_create_user, \
    _get_user, _save


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await _get_or_create_user(message)
    text_message = text(
        'This bot can help you ...',
        '/help - for information',
        sep='\n'
    )
    try:
        await message.answer(text_message)
    except BotBlocked:
        user = await _get_user(message.chat.id)
        user.is_active = False
        await _save(user)
