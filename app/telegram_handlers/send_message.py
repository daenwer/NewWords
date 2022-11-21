import os.path

from aiogram import Bot, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from asgiref.sync import async_to_sync

from NewWords.settings import TELEGRAM_TOKEN, BASE_DIR
from app.management.commands.bot import dp

inline_btn_add = InlineKeyboardButton('next', callback_data='next')
inline_kb_full = InlineKeyboardMarkup(row_width=1).add(inline_btn_add)


@async_to_sync
async def send_message(channel_id: int, text_message: str, audio_path: str):
    from app.telegram_handlers.text import get_prepared_phrase
    bot = Bot(token=TELEGRAM_TOKEN)
    # TODO: переписать на конкретные ошибки
    try:
        if audio_path:
            path = os.path.join(BASE_DIR, 'app', 'static', 'audio', audio_path)
            await bot.send_voice(
                chat_id=channel_id, voice=open(path, 'rb'),
                caption=get_prepared_phrase(text_message),
                reply_markup=inline_kb_full, parse_mode=ParseMode.MARKDOWN
            )
        else:
            await bot.send_message(
                chat_id=channel_id, text=get_prepared_phrase(text_message),
                reply_markup=inline_kb_full, parse_mode=ParseMode.MARKDOWN
            )
    except:
        from app.telegram_handlers.sync_async import _get_user, _save
        user = await _get_user(channel_id)
        user.is_active = False
        await _save(user)
    session = await bot.get_session()
    await session.close()


@dp.callback_query_handler(lambda c: c.data == 'next')
async def process_callback_delete(callback_query: types.CallbackQuery):
    from app.telegram_handlers.sync_async import (
        _send_next_phrase, _set_next_repeat_current_task
    )

    try:
        await callback_query.message.delete_reply_markup()
        await _set_next_repeat_current_task(callback_query.message)
        await _send_next_phrase(callback_query.message.chat.id)
    except:
        pass
