from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.db.models import Count
from .models import ForecastPrice, StockDb, TickerViewCount
from .views import TickerView
from channels.db import database_sync_to_async
from asyncio import sleep
import datetime
import numpy as np


class ChartConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        ticker_id = self.scope['url_route']['kwargs']['ticker_id'].upper()
        total_forecast = await self.get_forecast(ticker_id)
        get_viewcount = await self.get_viewcount(ticker_id)
        total_viewcount = get_viewcount[0]
        viewcount_data = get_viewcount[1]

        tkv = TickerView()
        if datetime.datetime.now() >= tkv.get_date_variables()[3]:
            form_forecast_date_T1 = tkv.get_date_variables()[0]
            form_forecast_date_T3 = tkv.get_date_variables()[1]
        else:
            if tkv.get_date_variables()[4].isoweekday() in set((6, 7)):
                form_forecast_date_T1 = tkv.get_date_variables()[0]
                form_forecast_date_T3 = tkv.get_date_variables()[1]
            else:
                form_forecast_date_T1 = tkv.get_date_variables()[4]
                form_forecast_date_T3 = tkv.next_4_day_calculator(form_forecast_date_T1)

        # next_day = TickerView.next_day_calculator(self, current_day=today)
        # next_day = datetime.date(2022, 12, 13)

        get_comm_forecast = await self.get_community_forecast(ticker_id = ticker_id, forecast_date_T1 = form_forecast_date_T1)
        # comm_pos_percent_T1 = await round(get_comm_forecast[0]*100, ndigits=1)
        # comm_neg_percent_T1 = await round(get_comm_forecast[1]*100, ndigits=1)
        # comm_pos_percent_T3 = await round(get_comm_forecast[2]*100, ndigits=1)
        # comm_neg_percent_T3 = await round(get_comm_forecast[3]*100, ndigits=1)
        
        await self.channel_layer.group_add(
            ticker_id,
            self.channel_name
        )
        await self.accept()
        
        await self.channel_layer.group_send(
            ticker_id,
            {
                "type": "view_count",
                "data": json.dumps({
                    'value': viewcount_data,
                    'total_viewcount': total_viewcount,
                    'total_forecast': total_forecast,
                    'comm_pos_percent_T1': get_comm_forecast[0],
                    'comm_neg_percent_T1': get_comm_forecast[1],
                    'comm_pos_percent_T3': get_comm_forecast[2],
                    'comm_neg_percent_T3': get_comm_forecast[3]
                    })
            }
        )
        await sleep(5)

    def date_to_str(self, price_date):
        return price_date.strftime("%d/%m/%Y")

    async def view_count(self, event):
        await self.send(event['data'])

    @database_sync_to_async
    def get_viewcount(self, ticker_id):
        viewcount = TickerViewCount.objects.filter(ticker=ticker_id)
        total_viewcount = viewcount.count()
        daily_viewcount = viewcount.extra({'created_date':"date(created)"}).values('created_date').annotate(created_count = Count('ticker')).order_by('created_date')
        viewcount_data = list(daily_viewcount.values_list('created_count', flat=True))
        return total_viewcount, viewcount_data

    @database_sync_to_async
    def get_forecast(self, ticker_id):
        return ForecastPrice.objects.filter(ticker=ticker_id).count()

    @database_sync_to_async
    def get_community_forecast(self, ticker_id, forecast_date_T1):
        comm_forecast_qs = ForecastPrice.objects.filter(ticker = ticker_id, forecast_date_T1 = forecast_date_T1).exclude(soier__username = "AI")
        if comm_forecast_qs.exists():
            comm_forecast_count = comm_forecast_qs.count()
            comm_pos_count_T1 = comm_forecast_qs.filter(forecast_movement_T1 = 1).count()
            comm_neg_count_T1 = comm_forecast_qs.filter(forecast_movement_T1 = -1).count()
            comm_pos_count_T3 = comm_forecast_qs.filter(forecast_movement_T3 = 1).count()
            comm_neg_count_T3 = comm_forecast_qs.filter(forecast_movement_T3 = -1).count()
            comm_pos_percent_T1 = round(comm_pos_count_T1/comm_forecast_count*100, ndigits=1)
            comm_neg_percent_T1 = round(comm_neg_count_T1/comm_forecast_count*100, ndigits=1)
            comm_pos_percent_T3 = round(comm_pos_count_T3/comm_forecast_count*100, ndigits=1)
            comm_neg_percent_T3 = round(comm_neg_count_T3/comm_forecast_count*100, ndigits=1)
        else:
            comm_pos_percent_T1 = 0
            comm_neg_percent_T1 = 0
            comm_pos_percent_T3 = 0
            comm_neg_percent_T3 = 0
        return comm_pos_percent_T1, comm_neg_percent_T1, comm_pos_percent_T3, comm_neg_percent_T3
    


    # async def send_data(self, event):
    #     for i in range (100):
    #         await self.send({
    #             "type": "websocket.send",
    #             "text": json.dumps({
    #                 'value': i
    #             })
    #         })
    #         await sleep(1)
    
    
