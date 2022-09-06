# import datetime
# import json
#
# from django_celery_beat.models import PeriodicTask, IntervalSchedule
#
# from NewWords.settings import CELERY_BEAT_SCHEDULER_CHECK
#
#
# def create_new_task():
#     PeriodicTask.objects.create(
#         name='Repeat user phrase',
#         task='repeat_phrase',
#         interval=IntervalSchedule.objects.get(
#             every=CELERY_BEAT_SCHEDULER_CHECK, period=IntervalSchedule.SECONDS
#         ),
#         # interval=IntervalSchedule.objects.get(every=10, period='seconds'),
#         # args=json.dumps([1][0]),
#         # start_time=timezone.now(),
#         start_time=timezone.now(),
#     )
