# Generated by Django 4.0 on 2022-08-01 15:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0047_alter_tickerviewcount_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tickerviewcount',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 1, 22, 43, 24, 659170)),
        ),
    ]
