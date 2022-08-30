from aiogram import types
from app.management.commands.bot import bot, dp
from app.telegram_handlers.sync_with_async import _user_get_or_create


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await _user_get_or_create(message)
    text_message = (
        '/help - get all commands\n'
        'send a message - add a word or phrase\n'
        '/admin - change bot settings and phrases\n'
        'ADDED SOME ELSE'
    )
    await bot.send_message(message.chat.id, text_message)
