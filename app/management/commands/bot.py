from django.core.management.base import BaseCommand
from NewWords.settings import TELEGRAM_TOKEN

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

# import tracemalloc
#
# tracemalloc.start()


bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        from app.telegram_handlers.start import start_command
        from app.telegram_handlers.help import help_command
        # from app.telegram_handlers.admin import admin_command
        from app.telegram_handlers.text import text_command
        executor.start_polling(dp)

