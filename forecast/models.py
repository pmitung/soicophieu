from time import timezone
from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User
import datetime
import pandas as pd
import numpy as np
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_init
from pmdarima import auto_arima
import logging
from django.db.models import Q
from ckeditor.fields import RichTextField
from django.utils import timezone

# User = settings.AUTH_USER_MODEL
class TickerList(models.Model):
    company_id = models.CharField(max_length=50, null=False, blank=False)
    ticker = models.CharField(max_length=50, null=False, blank=False, primary_key=True)
    code_id = models.CharField(max_length=50, null=False, blank=False)
    ex = models.CharField(max_length=50, null=False, blank=False)
    company_name =  models.TextField(null=False, blank=False)
    view_count = models.IntegerField(null = False, blank = True, default=0)
    comment_count = models.IntegerField(null = False, blank = True, default=0)
    forecast_count = models.IntegerField(null = False, blank = True, default=0)

class StockDb(models.Model):
    ticker = models.ForeignKey(
        'TickerList',
        on_delete=models.CASCADE,
    )
    price_date = models.DateField(null=False, blank=False)
    open_price = models.FloatField(null=False, blank=False)
    high_price = models.FloatField(null=False, blank=False)
    low_price = models.FloatField(null=False, blank=False)
    eod_price = models.FloatField(null=False, blank=False)
    volumn = models.BigIntegerField(null=False, blank=False)

class ForecastTrigger(models.Model):
    current_date = models.DateField(null=True, blank=False)
    forecast_date_T1 = models.DateField(null=True, blank=False)
    forecast_date_T3 = models.DateField(null = True, blank=False)

@receiver(post_save, sender = ForecastTrigger)
def update_forecast(sender, instance, **kwargs):
    today_ticker = list(StockDb.objects.filter(price_date = instance.current_date).values_list('ticker', flat=True))
    ticker_to_forecast = [entry for entry in today_ticker if len(StockDb.objects.filter(ticker = entry)) >= 4]

    forecast_batch = []
    forecast_batch_export = []
    daily_binary_batch = []
    daily_binary_batch_export = []
    user_performance = []
    user_performance_export = []

    for ticker in ticker_to_forecast:
        stockdb_query = StockDb.objects.filter(ticker = ticker).order_by('price_date')
        current_eod_price = stockdb_query[len(stockdb_query)-1].eod_price
        prev_eod_price = stockdb_query[len(stockdb_query)-2].eod_price
        T3_prev_eod_price = stockdb_query[len(stockdb_query)-4].eod_price

        # calculate daily binary model
        if current_eod_price > prev_eod_price:
            movement_T1 = 1
        elif current_eod_price < prev_eod_price:
            movement_T1 = -1
        else:
            movement_T1 = 0

        if current_eod_price > T3_prev_eod_price:
            movement_T3 = 1
        elif current_eod_price < T3_prev_eod_price:
            movement_T3 = -1
        else:
            movement_T3 = 0
        
        new_daily_binary = DailyBinary(ticker = TickerList.objects.get(ticker = ticker), price_date = instance.current_date, movement_T1 = movement_T1, movement_T3 = movement_T3)
        daily_binary_batch.append(new_daily_binary)
        daily_binary_batch_export.append({'ticker_id':ticker, 'price_date':instance.current_date, 'movement_T1':movement_T1, 'movement_T3':movement_T3})


        # calculate forecasted value
        forecast_date_T1 = instance.forecast_date_T1
        forecast_date_T3 = instance.forecast_date_T3

        if len(stockdb_query) >= 365:
            df = pd.DataFrame(stockdb_query.values()).tail(min(360, len(stockdb_query)))
            df_eod = df['eod_price'].to_frame()
            print(ticker, " start forecasting!")

            forecast_model = build_model(df_eod)
            forecast_values = forecast(4, forecast_model)
            forecast_eod_T1 = forecast_values[0]
            forecast_eod_T3 = forecast_values[3]
         
            if forecast_eod_T1 > current_eod_price:
                forecast_movement_T1 = 1
            elif forecast_eod_T1 == current_eod_price:
                forecast_movement_T1 = 0
            else:
                forecast_movement_T1 = -1

            if forecast_eod_T3 > current_eod_price:
                forecast_movement_T3 = 1
            elif forecast_eod_T3 == current_eod_price:
                forecast_movement_T3 = 0
            else:
                forecast_movement_T3 = -1
            new_forecast = ForecastPrice(
                ticker = TickerList.objects.get(ticker = ticker), 
                soier = User.objects.get(username = "AI"), 
                forecast_date_T1 = forecast_date_T1,
                forecast_date_T3 = forecast_date_T3,
                forecast_eod_T1 = forecast_eod_T1,
                forecast_eod_T3 = forecast_eod_T3,
                forecast_movement_T1 = forecast_movement_T1,
                forecast_movement_T3 = forecast_movement_T3)
            forecast_batch.append(new_forecast)
            forecast_batch_export.append({
                'ticker_id':ticker, 
                'soier_id':'AI', 
                'forecast_date_T1':forecast_date_T1,
                'forecast_date_T3':forecast_date_T3,
                'forecast_eod_T1':forecast_eod_T1,
                'forecast_eod_T3':forecast_eod_T3,
                'forecast_movement_T1':forecast_movement_T1,
                'forecast_movement_T3':forecast_movement_T3})
            logging.info(datetime.datetime.now(), ticker, " forecast completed!")
        else:
            logging.info("Data is not sufficient for forecasting")
        
        # evaluate the performance
        latest_forecast_query = ForecastPrice.objects.filter(forecast_date_T1 = instance.current_date).filter(ticker = ticker).order_by('soier_id')
        actual_movement = [movement_T1, movement_T3]

        if latest_forecast_query.exists():
            latest_forecast_df = pd.DataFrame(latest_forecast_query.values())[['forecast_movement_T1', 'forecast_movement_T3']]
            daily_performance = latest_forecast_df - actual_movement

            for i in range(0, len(daily_performance)):
                user_performance.append(UserPerformance(user = User.objects.get(id = latest_forecast_query[i].soier_id), 
                                                            ticker = TickerList.objects.get(ticker = ticker), 
                                                            evaluation_date = instance.price_date, 
                                                            performance_T1 = daily_performance.iloc[i, 0], 
                                                            performance_T3 = daily_performance.iloc[i, 1]))
                user_performance_export.append({
                    'user_id':User.objects.get(id = latest_forecast_query[i].soier_id).username,
                    'ticker':ticker,
                    'evaluation_date':instance.price_date,
                    'performance_T1':daily_performance.iloc[i, 0],
                    'performance_T3':daily_performance.iloc[i, 1]
                })
        else:
            logging.info('There is no forecast on this date')
    
    DailyBinary.objects.bulk_create(daily_binary_batch)
    ForecastPrice.objects.bulk_create(forecast_batch)
    UserPerformance.objects.bulk_create(user_performance)

    daily_binary_batch_export = pd.DataFrame(daily_binary_batch_export)
    forecast_batch_export = pd.DataFrame(forecast_batch_export)
    user_performance_export = pd.DataFrame(user_performance_export)

    daily_binary_batch_export.to_excel('daily_binary_batch_export.xlsx', index=False)
    forecast_batch_export.to_excel('forecast_batch_export.xlsx', index=False)
    user_performance_export.to_excel('user_performance_export.xlsx', index=False)

def build_model(df_y):
    model = auto_arima(df_y, error_action="ignore", suppress_warnings=True)
    return model

def forecast(n_periods, model):
    forecast = model.predict(n_periods=n_periods)
    return np.ndarray.round(forecast, decimals=2)


class DailyBinary(models.Model):
    ticker = models.ForeignKey(
        'TickerList',
        on_delete=models.CASCADE,
    )
    price_date = models.DateField(null=False, blank=False)
    movement_T1 = models.FloatField(null = False, blank=False)
    movement_T3 = models.FloatField(null=True, blank=True)

class StockDbBuffer(models.Model):
    ticker = models.CharField(max_length=50, null=False, blank=False)
    price_date = models.DateField(null=False, blank=False)
    open_price = models.FloatField(null=False, blank=False)
    high_price = models.FloatField(null=False, blank=False)
    low_price = models.FloatField(null=False, blank=False)
    eod_price = models.FloatField(null=False, blank=False)
    volumn = models.BigIntegerField(null=False, blank=False)
    # match_key = models.CharField(max_length=50, null=False, blank=False)

class ForecastPrice(models.Model):
    ticker = models.ForeignKey(
        'TickerList',
        on_delete=models.CASCADE,
    )
    soier = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    forecast_high_T1 = models.FloatField(null=True, blank=True)
    forecast_low_T1 = models.FloatField(null=True, blank=True)
    forecast_eod_T1 = models.FloatField(null=True, blank=True)
    forecast_eod_T3 = models.FloatField(null=True, blank=True)
    forecast_movement_T1 = models.FloatField(null=True, blank=True)
    forecast_movement_T3 = models.FloatField(null=True, blank=True)
    forecast_date_T1 = models.DateField(null=True, blank=True)
    forecast_date_T3 = models.DateField(null=True, blank=True)
    created_at = models.DateField(null = True, blank = True, auto_now_add=True) #need to come back for get logic
    updated_times = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.updated_times += 1
        return super(ForecastPrice, self).save(*args, **kwargs)

class UserPerformance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.ForeignKey('TickerList', on_delete=models.CASCADE)
    evaluation_date = models.DateField(null = True, blank=True)
    performance_T1 = models.BooleanField(null=True, blank=True)
    performance_T3 = models.BooleanField(null=True, blank=True)

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    display_name = models.CharField(max_length=30, null=True, blank=True)
    bio = RichTextField(null=True, blank = True)
    zalo_room = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=15,  null=True, blank=True, unique=True)
    avatar =  models.ImageField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)


    def rank_forecaster(self):
        if UserPerformance.objects.filter(user__username=self.user).exists():
            forecaster_qs = UserPerformance.objects.filter(user__username = self.user)
            number_of_forecast = forecaster_qs.count()
            number_of_true_all = forecaster_qs.filter(Q(performance_T1 = 1)|Q(performance_T3 = 1)).count()
            number_of_true_T1 = forecaster_qs.filter(performance_T1 = 1).count()
            number_of_true_T3 = forecaster_qs.filter(performance_T3 = 1).count()

            pfm_all = number_of_true_all/number_of_forecast
            pfm_T1 = number_of_true_T1/number_of_forecast
            pfm_T3 = number_of_true_T3/number_of_forecast
            return (pfm_all, pfm_T1, pfm_T3)
        else:
            return(0, 0, 0)

    def _get_reputation(self):
        base_reputation = 100
        obj_forecast = ForecastPrice.objects.filter(soier = self.user)
        obj_pfm = self.rank_forecaster()
        pfm_T1_add = obj_pfm[1]*base_reputation*1
        pfm_T3_add = obj_pfm[2]*base_reputation*1.5
        reputation_point = base_reputation + obj_forecast.count()*1.5 + pfm_T1_add + pfm_T3_add
        return round(reputation_point, ndigits=2) 

    reputation = property(_get_reputation)
    pfm_all = property(rank_forecaster)

@receiver(post_init, sender = UserProfile)
def set_default_display_name(sender, instance, *args, **kwargs):
    if not instance.display_name:
        instance.display_name = instance.user.username

@receiver(post_save, sender = User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user = instance)

@receiver(post_save, sender = User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class UserFollowing(models.Model):
    user_id = models.ForeignKey(User, related_name="following", on_delete=CASCADE)
    follower_id = models.ForeignKey(User, related_name="followers", on_delete=CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'follower_id')

class TickerFollowing(models.Model):
    ticker_id = models.ForeignKey('TickerList', related_name='ticker_follow', on_delete=CASCADE)
    follower_id = models.ForeignKey(User, related_name='ticker_follower', on_delete=CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ticker_id', 'follower_id')

class Post(models.Model):
    soier = models.ForeignKey(User, on_delete=CASCADE)
    post = models.TextField()
    post_time = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    soier = models.ForeignKey(User, on_delete=CASCADE)
    ticker = models.ForeignKey('TickerList', on_delete=CASCADE)
    content = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-comment_time']

    def __str__(self):
        return 'Comment by {}'.format(self.soier)

    def children(self):
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True

class TickerViewCount(models.Model):
    ticker = models.ForeignKey('TickerList', related_name='tickerviewcount', on_delete=CASCADE)
    ip = models.CharField(max_length=40)
    session = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length = 255, null=True, blank=True)

