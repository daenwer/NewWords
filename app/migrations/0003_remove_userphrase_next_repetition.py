# Generated by Django 3.2.15 on 2022-09-13 22:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_remove_userphrase_in_work'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userphrase',
            name='next_repetition',
        ),
    ]