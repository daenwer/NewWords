import datetime
from time import sleep

from django.core.management.base import BaseCommand
from NewWords.settings import SLEEP_START_TIME, SLEEP_END_TIME
from app.models.base import RepeatSchedule
from app.tasks import create_new_celery_task


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        while True:
            current_datetime = datetime.datetime.now()
            sleep(10)

            if SLEEP_START_TIME < current_datetime.time() < SLEEP_END_TIME:
                continue

            current_tasks = RepeatSchedule.objects.filter(
                is_active=True, next_repeat__lte=current_datetime
            )
            for task in current_tasks:
                # create_new_celery_task.delay(task.id)
                create_new_celery_task(task.id)
