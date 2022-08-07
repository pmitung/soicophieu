# Generated by Django 4.0 on 2022-03-13 16:25

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockDbBuffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=50)),
                ('price_date', models.DateField()),
                ('open_price', models.FloatField()),
                ('high_price', models.FloatField()),
                ('low_price', models.FloatField()),
                ('eod_price', models.FloatField()),
                ('volumn', models.BigIntegerField()),
                ('match_key', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TickerList',
            fields=[
                ('company_id', models.CharField(max_length=50)),
                ('ticker', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('code_id', models.CharField(max_length=50)),
                ('ex', models.CharField(max_length=50)),
                ('company_name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='StockDb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_date', models.DateField()),
                ('open_price', models.FloatField()),
                ('high_price', models.FloatField()),
                ('low_price', models.FloatField()),
                ('eod_price', models.FloatField()),
                ('volumn', models.BigIntegerField()),
                ('ticker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecast.tickerlist')),
            ],
        ),
        migrations.CreateModel(
            name='SoierPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('performance_date', models.DateField(default=datetime.datetime.now)),
                ('soier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='Posts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.TextField()),
                ('post_time', models.DateTimeField(auto_now_add=True)),
                ('soier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='ForecastPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('forecast_high_T1', models.IntegerField()),
                ('forecast_low_T1', models.IntegerField()),
                ('forecast_eod_T1', models.IntegerField()),
                ('forecast_summary_T1', models.CharField(max_length=10)),
                ('forecast_date', models.DateTimeField(default=datetime.datetime.now)),
                ('soier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
                ('ticker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecast.tickerlist')),
            ],
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('comment_time', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='forecast.comments')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='forecast.posts')),
                ('soier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
    ]
