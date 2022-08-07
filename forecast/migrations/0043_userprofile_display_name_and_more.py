# Generated by Django 4.0 on 2022-07-30 15:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0042_remove_userprofile_email_remove_userprofile_facebook_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='display_name',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='tickerviewcount',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 30, 22, 16, 6, 701852)),
        ),
    ]
