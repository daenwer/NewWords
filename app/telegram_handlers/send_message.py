from aiogram import Bot
from asgiref.sync import async_to_sync

from NewWords.settings import TELEGRAM_TOKEN


@async_to_sync
async def send_message(channel_id: int, text: str):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=channel_id, text=text)
    session = await bot.get_session()
    await session.close()
