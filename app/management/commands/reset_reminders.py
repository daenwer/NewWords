from django.core.management.base import BaseCommand
from app.models.base import UserSchedule


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        reminders = UserSchedule.objects.all()
        for reminder in reminders:
            try:
                reminder.send_on_schedule = True
                reminder.current_message_id = None
                reminder.save()
            except Exception as e:
                print(f'UserScheduler = {reminder.id}. Problem: {e}')
