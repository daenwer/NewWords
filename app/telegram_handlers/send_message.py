import os.path

from aiogram import Bot
from asgiref.sync import async_to_sync

from NewWords.settings import TELEGRAM_TOKEN, BASE_DIR


@async_to_sync
async def send_message(channel_id: int, text: str, audio_path: str):
    bot = Bot(token=TELEGRAM_TOKEN)
    # TODO: переписать на конкретные ошибки
    try:
        if audio_path:
            path = os.path.join(BASE_DIR, 'app', 'static', 'audio', audio_path)
            await bot.send_voice(
                chat_id=channel_id, voice=open(path, 'rb'), caption=text
            )
        else:
            await bot.send_message(chat_id=channel_id, text=text)
    except:
        from app.telegram_handlers.sync_async import _get_user, _save
        user = await _get_user(channel_id)
        user.is_active = False
        await _save(user)
    session = await bot.get_session()
    await session.close()
