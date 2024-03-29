import re

from aiogram.utils.markdown import text, bold

from app.telegram_handlers.sync_async import _get_user, _save, update_phrase, \
    _get_phrase
from asyncio import sleep

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from aiogram.utils.exceptions import BotBlocked, MessageToDeleteNotFound

from app.management.commands.bot import bot, dp

inline_btn_delete = InlineKeyboardButton('cancel', callback_data='cancel')
inline_btn_add = InlineKeyboardButton('edit', callback_data='edit')
inline_kb_full = InlineKeyboardMarkup(row_width=2).add(
    inline_btn_delete, inline_btn_add
)


@dp.message_handler(commands=['edit'])
async def edit_command(message: types.Message):

    user = await _get_user(message.chat.id)
    if not user:
        await message.answer('First execute\n/start')
        return

    if not message.reply_to_message:
        return

    old_phrase = message.reply_to_message.html_text
    if 'Added -&gt;' in old_phrase:
        old_phrase = old_phrase.split('Added -&gt;')[1].strip()

    if (
        '/help' in old_phrase
    ) or (
        '/start' in old_phrase
    ) or (
        '/admin' in old_phrase
    ):
        return

    if not await _get_phrase(old_phrase):
        await message.answer(
            "You want to change an entry that doesn't exist!"
        )
        return

    new_phrase = message.text.split('/edit')[1].strip()

    is_allowed = not bool(re.search(r"[^a-zA-Z .,':!?-]", new_phrase))

    if len(message.text) > 511:
        await message.answer(
            'The phrase must not be longer than 512 characters!'
        )
        return

    elif not is_allowed:
        await message.answer(
            "Phrases can only consist of English letters and contain .,':!?-"
        )
        return

    if new_phrase == old_phrase:
        await message.answer('These are the same phrases.')
        return

    disable_user = False
    try:
        new_message = await bot.send_message(
            message.chat.id,
            text(bold('change'), old_phrase, bold('to'), new_phrase, sep='\n'),
            reply_markup=inline_kb_full, parse_mode=ParseMode.MARKDOWN

        )
    except BotBlocked:
        disable_user = True

    await bot.delete_message(
        chat_id=message.chat.id, message_id=message.message_id
    )

    if disable_user:
        user = await _get_user(message.chat.id)
        user.is_active = False
        await _save(user)
        return

    await sleep(60)
    try:
        await bot.delete_message(
            chat_id=new_message.chat.id, message_id=new_message.message_id
        )
    except MessageToDeleteNotFound:
        pass


@dp.callback_query_handler(lambda c: c.data == 'cancel')
async def process_callback_delete(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    try:
        await callback_query.message.delete()
    except:
        pass


@dp.callback_query_handler(lambda c: c.data == 'edit')
async def process_callback_delete(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await update_phrase(callback_query)
    try:
        await callback_query.message.delete()
    except:
        pass
    await bot.send_message(
        callback_query.from_user.id, f'Edited -> {callback_query.message.text}'
    )
