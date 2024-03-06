# Generated by Django 3.2.15 on 2022-12-04 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20221029_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='userschedule',
            name='current_message_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Current message id'),
        ),
        migrations.AlterField(
            model_name='phrase',
            name='value',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Word or phrase'),
        ),
        migrations.AlterField(
            model_name='userschedule',
            name='send_on_schedule',
            field=models.BooleanField(default=True, verbose_name='Send on schedule'),
        ),
    ]
