# Generated by Django 4.0 on 2022-04-17 14:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('forecast', '0011_alter_forecastprice_forecast_eod_t1_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='forecastprice',
            old_name='forecast_summary_T1',
            new_name='forecast_movement_T1',
        ),
       
    ]
