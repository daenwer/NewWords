import os
import re
from asyncio import sleep

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import BotBlocked, MessageToDeleteNotFound

from NewWords.settings import BASE_DIR
from app.telegram_handlers.sync_async import add_new_phrase, _get_user, _save, \
    _get_phrase, _download_pronunciation_task

from app.management.commands.bot import bot, dp

inline_btn_delete = InlineKeyboardButton('delete', callback_data='delete')
inline_btn_add = InlineKeyboardButton('add', callback_data='add')
inline_kb_full = InlineKeyboardMarkup(row_width=2).add(
    inline_btn_delete, inline_btn_add
)


@dp.message_handler()
async def text_command(message: types.Message):

    user = await _get_user(message.chat.id)
    if not user:
        await message.answer('First execute\n/start')
        return

    if message.reply_to_message:
        return

    text_message = message.text

    is_allowed = not bool(
        re.search(r"[^a-zA-Z )(///n//t.,*':!?-]", text_message)
    )

    if len(message.text) < 511 and is_allowed:
        args = (message.chat.id, text_message)
        kwargs = {'reply_markup': inline_kb_full}
    elif len(message.text) > 511:
        args = (
            message.chat.id,
            'The phrase must not be longer than 512 characters!'
        )
        kwargs = {}
    elif not is_allowed:
        args = (
            message.chat.id,
            "Phrases can only consist of English letters and contain .,*':!?-"
        )
        kwargs = {}

    disable_user = False
    try:
        new_message = await bot.send_message(*args, **kwargs)
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


@dp.callback_query_handler(lambda c: c.data == 'delete')
async def process_callback_delete(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    try:
        await callback_query.message.delete()
    except:
        pass


@dp.callback_query_handler(lambda c: c.data == 'add')
async def process_callback_delete(callback_query: types.CallbackQuery):

    await bot.answer_callback_query(callback_query.id)
    await add_new_phrase(callback_query)
    phrase = await _get_phrase(callback_query.message.text)

    disable_user = False
    try:
        await callback_query.message.delete_reply_markup()
    except BotBlocked:
        disable_user = True

    if disable_user:
        user = await _get_user(callback_query.message.chat.id)
        user.is_active = False
        await _save(user)
        return

    await _download_pronunciation_task(phrase.id)
    # await sleep(3)
    phrase = await _get_phrase(phrase.value)
    await callback_query.message.delete()
    if phrase.pronunciation:
        path = os.path.join(
            BASE_DIR, 'app', 'static', 'audio', phrase.pronunciation
        )
        await bot.send_voice(
            chat_id=callback_query.message.chat.id,
            voice=open(path, 'rb'), caption=phrase.value,
        )
    else:
        await bot.send_message(
            callback_query.from_user.id,
            f'Added -> {callback_query.message.text}'
        )
