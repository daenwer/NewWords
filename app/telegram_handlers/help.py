from aiogram import types
from aiogram.utils.exceptions import BotBlocked

from app.management.commands.bot import bot, dp
from app.telegram_handlers.sync_async import _get_user, _save


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    text_message = (
        '/help - get all commands\n'
        'send a message - add a word or phrase\n'
        '/admin - change bot settings and phrases\n'
        'ADDED SOME ELSE'
    )
    try:
        await bot.send_message(message.chat.id, text_message)
    except BotBlocked:
        user = await _get_user(message.chat.id)
        user.is_active = False
        await _save(user)
