from aiogram import types
from app.management.commands.bot import bot, dp
from app.telegram_handlers.sync_with_async import _user_get_or_create


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await _user_get_or_create(message)
    text_message = (
        'This bot can help you ...\n'
        '/help - for information'
    )
    await bot.send_message(message.chat.id, text_message)
