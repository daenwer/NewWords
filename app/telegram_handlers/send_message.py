import os.path
from asyncio import sleep

from aiogram import Bot, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import MessageToDeleteNotFound
from asgiref.sync import async_to_sync

from NewWords.settings import TELEGRAM_TOKEN, BASE_DIR
from app.management.commands.bot import dp

inline_btn_add = InlineKeyboardButton('next', callback_data='next')
inline_kb_full = InlineKeyboardMarkup(row_width=1).add(inline_btn_add)


@async_to_sync
async def send_message(channel_id: int, text: str, audio_path: str):
    from app.telegram_handlers.sync_async import (
        _get_user, _save, _resend_message, _change_user_schedule,
        _current_message_status_is_active
    )

    bot = Bot(token=TELEGRAM_TOKEN)
    message = None
    # TODO: переписать на конкретные ошибки
    try:
        if audio_path:
            path = os.path.join(BASE_DIR, 'app', 'static', 'audio', audio_path)
            message = await bot.send_voice(
                chat_id=channel_id, voice=open(path, 'rb'), caption=text,
                reply_markup=inline_kb_full
            )
        else:
            message = await bot.send_message(chat_id=channel_id, text=text)
    except:
        user = await _get_user(channel_id)
        user.is_active = False
        await _save(user)
    if message:
        await _change_user_schedule(
            chat_id=channel_id, send_on_schedule=False,
            current_message_id=message.message_id
        )
        await sleep(1800)
        if await _current_message_status_is_active(
            channel_id, message.message_id
        ):
            try:
                await bot.delete_message(
                    chat_id=channel_id, message_id=message.message_id
                )
                await _resend_message(channel_id, text, audio_path)
            except MessageToDeleteNotFound:
                pass
        else:
            try:
                await bot.edit_message_reply_markup(
                    channel_id, message.message_id
                )
            except:
                pass
    session = await bot.get_session()
    await session.close()


@dp.callback_query_handler(lambda c: c.data == 'next')
async def process_callback_delete(callback_query: types.CallbackQuery):
    from app.telegram_handlers.sync_async import (
        _send_next_phrase, _set_next_repeat_current_task,
        _current_message_status_is_active
    )

    try:
        await callback_query.message.delete_reply_markup()
        await _set_next_repeat_current_task(callback_query.message)
        if await _current_message_status_is_active(
            callback_query.message.chat.id, callback_query.message.message_id
        ):
            await _send_next_phrase(callback_query.message.chat.id)
    except:
        pass
