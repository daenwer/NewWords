# Generated by Django 3.2.15 on 2022-09-05 23:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userphrase',
            name='in_work',
        ),
    ]
