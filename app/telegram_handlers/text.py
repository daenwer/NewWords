from asyncio import sleep

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.telegram_handlers.sync_with_async import add_new_phrase
from app.management.commands.bot import bot, dp
from app.telegram_handlers.sync_with_async import _user_get_or_create

inline_btn_delete = InlineKeyboardButton('delete', callback_data='delete')
inline_btn_add = InlineKeyboardButton('add', callback_data='add')
inline_kb_full = InlineKeyboardMarkup(row_width=2).add(
    inline_btn_delete, inline_btn_add
)


@dp.message_handler()
async def text_command(message: types.Message):
    await _user_get_or_create(message)
    text_message = (
        message.text
    )
    if len(message.text) < 511:
        new_message = await bot.send_message(
            message.chat.id, text_message, reply_markup=inline_kb_full
        )
    else:
        new_message = await bot.send_message(
            message.chat.id,
            'The phrase must not be longer than 512 characters!'
        )
    await bot.delete_message(
        chat_id=message.chat.id, message_id=message.message_id
    )
    await sleep(60)
    try:
        await bot.delete_message(
            chat_id=new_message.chat.id, message_id=new_message.message_id
        )
    # TODO: Exception
    except:
        pass


@dp.callback_query_handler(lambda c: c.data == 'delete')
async def process_callback_delete(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data == 'add')
async def process_callback_delete(callback_query: types.CallbackQuery):

    await bot.answer_callback_query(callback_query.id)
    await add_new_phrase(callback_query)
    await callback_query.message.delete()
    await bot.send_message(
        callback_query.from_user.id, f'Added -> {callback_query.message.text}'
    )
