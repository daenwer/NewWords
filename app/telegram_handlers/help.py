from aiogram import types
from aiogram.types import ParseMode
from aiogram.utils.exceptions import BotBlocked

from app.management.commands.bot import dp
from app.telegram_handlers.sync_async import _get_user, _save

from aiogram.utils.markdown import text, bold, italic, code, pre


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    text_message = text(bold('Список всех команд'),
        bold('/help') + ' - список всех команд',
        bold('New phrase') + ' - для добавления слова или фразы',
        'в reply напишите ' + '/edit Change phrase',
        # '/admin - change bot settings and phrases',
        # 'ADDED SOME ELSE',
        sep='\n'
    )
    try:
        await message.answer(text_message, parse_mode=ParseMode.MARKDOWN)
    except BotBlocked:
        user = await _get_user(message.chat.id)
        user.is_active = False
        await _save(user)
