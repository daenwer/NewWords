# import uuid
# import datetime
#
# from aiogram import types
# from aiogram.utils.exceptions import BotBlocked
#
# from app.telegram_handlers.sync_async import _get_user, _save
# from app.management.commands.bot import bot, dp
#
#
# @dp.message_handler(commands=['admin'])
# async def admin_command(message: types.Message):
#     user = await _get_user(message.chat.id)
#     if user:
#         user.token = uuid.uuid4()
#         user.date_create_token = datetime.datetime.now()
#         await _save(user)
#         text_message = (
#             # TODO: ссылка на урл с токеном сначала дописать)))
#             f'http://127.0.0.1:8000/login/{user.token}/'
#         )
#     else:
#         text_message = (
#             'Register please!)'
#         )
#     try:
#         await bot.send_message(message.chat.id, text_message)
#     except BotBlocked:
#         if user:
#             user.is_active = False
#             await _save(user)
