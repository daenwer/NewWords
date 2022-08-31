from datetime import date
from django.utils import timezone

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserSchedule(models.Model):
    class Meta:
        verbose_name = 'User schedule'
        verbose_name_plural = 'User schedules'

    def __str__(self):
        return (
            f'Settings for {self.user.full_name}'
            if hasattr(self, 'user') else 'Settings'
        )

    start_time = models.TimeField(default='10:00')
    finish_time = models.TimeField(default='23:00')
    repetition_1 = models.IntegerField(
        default=60*60, verbose_name='First repetition'
    )
    repetition_2 = models.IntegerField(
        default=60*60*8, verbose_name='Second repetition'
    )
    repetition_3 = models.IntegerField(
        default=60*60*24, verbose_name='Third repetition'
    )
    repetition_4 = models.IntegerField(
        default=60*60*24*3, verbose_name='Fourth repetition'
    )
    repetition_5 = models.IntegerField(
        default=60*60*24*7, verbose_name='Fifth repetition'
    )
    repetition_6 = models.IntegerField(
        default=60*60*24*21, verbose_name='Sixth repetition'
    )
    repetition_7 = models.IntegerField(
        default=60*60*24*90, verbose_name='Seventh repetition'
    )
    repetition_8 = models.IntegerField(
        default=60*60*24*180, verbose_name='Eighth repetition'
    )
    repetition_9 = models.IntegerField(
        default=60*60*24*360, verbose_name='Ninth repetition'
    )


class User(AbstractUser):
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = "Users"

    def __str__(self):
        return f'{self.full_name} ({self.username})'

    telegram_chat_id = models.IntegerField(
        verbose_name='ID Telegram chat', null=True, blank=True
    )
    user_schedule = models.ForeignKey(
        UserSchedule, verbose_name='UserSchedule', related_name='user_schedule',
        on_delete=models.CASCADE, null=True, blank=True
    )
    first_name = models.CharField(
        verbose_name='first name', max_length=150, blank=True, null=True
    )
    last_name = models.CharField(
        verbose_name='last name', max_length=150, blank=True, null=True
    )
    token = models.UUIDField(
        verbose_name='token', blank=True, null=True, unique=True
    )
    date_create_token = models.DateTimeField(null=True, blank=True)

    @property
    def full_name(self):
        return self.get_full_name()


class Phrase(models.Model):
    class Meta:
        verbose_name = 'Phrase'
        verbose_name_plural = 'Phrases'

    value = models.CharField(
        max_length=512, verbose_name='Word or phrase', null=True, blank=True
    )
    pronunciation = models.CharField(
        max_length=256, null=True, blank=True, verbose_name='Pronunciation'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='creator'
    )


def schedule_default():
    return {
        'schedule': (
            False, False, False, False, False, False, False, False, False
        )
    }


class UserPhrase(models.Model):
    class Meta:
        verbose_name = 'User phrase'
        verbose_name_plural = 'User phrases'

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user'
    )
    base_phrase = models.ForeignKey(
        Phrase, on_delete=models.CASCADE, related_name='phrase'
    )
    next_repetition = models.DateField(
        default=date.today,
        verbose_name='Next repetition'
    )
    repeat_schedule = models.JSONField(default=schedule_default)
    in_work = models.BooleanField(default=False)
