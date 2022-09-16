import os.path

from aiogram import Bot
from asgiref.sync import async_to_sync

from NewWords.settings import TELEGRAM_TOKEN, BASE_DIR


@async_to_sync
async def send_message(channel_id: int, text: str, audio_path: str):
    bot = Bot(token=TELEGRAM_TOKEN)

    if audio_path:
        path = os.path.join(BASE_DIR, 'app', 'static', 'audio', audio_path)
        await bot.send_voice(
            chat_id=channel_id, voice=open(path, 'rb'), caption=text
        )
    else:
        await bot.send_message(chat_id=channel_id, text=text)

    session = await bot.get_session()
    await session.close()
