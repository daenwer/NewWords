# Generated by Django 3.2.15 on 2022-09-21 00:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20220921_0048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_schedule',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user', to='app.userschedule', verbose_name='User Schedule'),
        ),
    ]
