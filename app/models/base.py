from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserQuerySet(models.query.QuerySet):
    def get_or_create(self, defaults=None, **kwargs):
        message = kwargs['message']
        user = User.objects.filter(
            telegram_chat_id=message.chat.id
        )
        if user:
            save = False
            user = user[0]
            if not user.is_active:
                user.is_active = True
                save = True
            if user.first_name != message.chat.first_name:
                user.first_name = message.chat.first_name
                save = True
            if user.last_name != message.chat.last_name:
                user.last_name = message.chat.last_name
                save = True
            if user.username != message.chat.username:
                user.username = message.chat.username
                save = True
            if save:
                user.refresh_from_db()
        else:
            user_schedule = UserSchedule.objects.create()
            user = User.objects.create(
                telegram_chat_id=message.chat.id,
                username=message.chat.username,
                first_name=message.chat.first_name,
                last_name=message.chat.last_name,
                user_schedule=user_schedule,
            )
        return user


class UserManager(models.Manager):
    def get_queryset(self):
        return UserQuerySet(self.model)

    def create_user(self, *args, **kwargs):
        return super().create_user(*args, **kwargs)

    def create_superuser(self, *args, **kwargs):
        return super().create_superuser(*args, **kwargs)


class UserSchedule(models.Model):
    class Meta:
        verbose_name = 'User schedule'
        verbose_name_plural = 'User schedules'

    def __str__(self):
        return (
            f'Settings for {self.user.full_name}'
            if hasattr(self, 'user') else 'Settings'
        )

    start_time = models.TimeField(default='9:00')
    repetition_1 = models.IntegerField(
        default=3600, verbose_name='First repetition'
    )
    repetition_2 = models.IntegerField(
        default=28800, verbose_name='Second repetition'
    )
    repetition_3 = models.IntegerField(
        default=86400, verbose_name='Third repetition'
    )
    repetition_4 = models.IntegerField(
        default=259200, verbose_name='Fourth repetition'
    )
    repetition_5 = models.IntegerField(
        default=604800, verbose_name='Fifth repetition'
    )
    repetition_6 = models.IntegerField(
        default=1814400, verbose_name='Sixth repetition'
    )
    repetition_7 = models.IntegerField(
        default=7776000, verbose_name='Seventh repetition'
    )
    repetition_8 = models.IntegerField(
        default=15552000, verbose_name='Eighth repetition'
    )
    repetition_9 = models.IntegerField(
        default=31104000, verbose_name='Ninth repetition'
    )


class User(AbstractUser):
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = "Users"

    objects = UserManager()

    def __str__(self):
        return f'{self.full_name} ({self.username})'

    telegram_chat_id = models.IntegerField(verbose_name='ID Telegram chat')

    user_schedule = models.ForeignKey(
        UserSchedule, verbose_name='UserSchedule', related_name='user_schedule',
        on_delete=models.CASCADE, null=True, blank=True
    )

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
