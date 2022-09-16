import datetime
from time import sleep

from django.core.management.base import BaseCommand
from NewWords.settings import SLEEP_START_TIME, SLEEP_END_TIME
from app.tasks import prepare_new_celery_tasks


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        while True:
            current_datetime = datetime.datetime.now()
            sleep(60)

            if SLEEP_START_TIME < current_datetime.time() < SLEEP_END_TIME:
                continue

            prepare_new_celery_tasks.delay()
            # prepare_new_celery_tasks()
