# Generated by Django 4.0 on 2022-08-17 00:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0052_alter_tickerviewcount_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tickerviewcount',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 17, 7, 23, 9, 293292)),
        ),
    ]
