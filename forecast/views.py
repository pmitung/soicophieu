from django.conf import settings
from django.db import IntegrityError
from django.views.generic import TemplateView
import datetime
from django.shortcuts import get_object_or_404, redirect
import pytz
from django.db.models import Count
import feedparser
import random
from django.db.models import Q
from django.contrib.auth.models import User
from .models import DailyBinary, StockDb, ForecastPrice, TickerFollowing, TickerList, TickerViewCount, UserFollowing, UserPerformance, UserProfile
from .forms import ProfileEditForm, SearchForm, TickerFollowForm, TickerUnfollow, UserForecastForm, FollowerForm
from django.contrib.auth.mixins import LoginRequiredMixin
from collections import Counter

class HomePageView(TemplateView):
    template_name = 'index.html'
    form_class = SearchForm

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = self.form_class(request.POST or None)
            if form.is_valid():
                ticker = form.cleaned_data['ticker_id']

            return redirect('tickerview', ticker=ticker)
            
    def date_to_str(self, price_date):
        return price_date.strftime("%d/%m/%Y")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        all_ticker = list(TickerList.objects.all().values_list('ticker', flat=True))

        recentview_ticker_qs = TickerViewCount.objects.filter(created__gte = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24))
        order_ticker_viewcount = recentview_ticker_qs.extra({'ticker':'ticker_id'}).values('ticker').annotate(ticker_count = Count('ticker_id')).order_by('-ticker_count')

        top_ticker_list = list(order_ticker_viewcount.values_list('ticker', flat=True))[:10]
        
        if "^VNINDEX" in top_ticker_list:
            top_ticker_list.remove("^VNINDEX")

        combine_ticker_list = []

        for entry in top_ticker_list:
            if DailyBinary.objects.filter(ticker__ticker=entry).exists():
                combine_ticker_list.append({'ticker':entry, 'movement_T1':DailyBinary.objects.filter(ticker__ticker=entry).latest('price_date').movement_T1})
            else:
                combine_ticker_list.append({'ticker':entry, 'movement_T1':2})

        forecaster_qs = UserProfile.objects.all().values_list('user__username', flat=True)
        top_forecaster_list = sorted([{'forecaster':forecaster, 'reputation':UserProfile.objects.get(user__username = forecaster).reputation} for forecaster in forecaster_qs], key=lambda d: d['reputation'], reverse=True)[:10]
        

        market_feeds = feedparser.parse('https://www.stockbiz.vn/RSS/News/TopStories.ashx')
        title_link_2 = [{'title': entry.title, 'link': entry.link} for entry in market_feeds.entries]
        if len(title_link_2) > 10:
            other_feeds = random.sample(title_link_2, 20)
        else:
            other_feeds = title_link_2[0:len(title_link_2)]

        display_feeds =  other_feeds

        vnindex_data = StockDb.objects.filter(ticker__ticker = '^VNINDEX').order_by('price_date')
        data_close = list(vnindex_data.values_list('eod_price', flat=True))
        labels = list(map(self.date_to_str, list(vnindex_data.values_list('price_date', flat=True))))
        if DailyBinary.objects.filter(ticker__ticker = '^VNINDEX').filter(price_date = DailyBinary.objects.latest('price_date').price_date).exists():
            vnindex_movement = DailyBinary.objects.get(ticker__ticker = "^VNINDEX", price_date = DailyBinary.objects.latest('price_date').price_date).movement_T1
        else:
            vnindex_movement = 2

        # list_followed_ticker = list(TickerFollowing.objects.all().values_list('ticker_id', flat=True))
        # followed_ticker_count = dict(Counter(list_followed_ticker))
        # top_followed_ticker = dict(sorted(followed_ticker_count.items(), key=lambda kv: (kv[1], kv[0]))[:20])

        # list_forecasted_ticker = list(ForecastPrice.objects.all().values_list('ticker__ticker', flat=True))
        # forecasted_ticker_count = dict(Counter(list_forecasted_ticker))
        # top_forecasted_ticker = list(sorted(forecasted_ticker_count.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:20])

        # list_top_forecasted_ticker = []

        # for entry in top_forecasted_ticker:
        #     if DailyBinary.objects.filter(ticker__ticker = entry[0]).exists():
        #         list_top_forecasted_ticker.append({'ticker':entry[0], 'count':entry[1], 'movement_T1':DailyBinary.objects.filter(ticker__ticker=entry[0]).latest('price_date').movement_T1})
        #     else:
        #         list_top_forecasted_ticker.append({'ticker':entry[0], 'count':entry[1], 'movement_T1':2})


        top_stock_data = []
        for entry in top_ticker_list[:5]:
            stock_data = StockDb.objects.filter(ticker__ticker = entry).order_by('price_date')
            if DailyBinary.objects.filter(ticker__ticker = entry).filter(price_date = DailyBinary.objects.latest('price_date').price_date).exists():
                top_stock_data.append({
                    'ticker': entry,
                    'company': TickerList.objects.get(ticker=entry).company_name,
                    'labels': list(map(self.date_to_str, list(stock_data.values_list('price_date', flat=True)))),
                    'data_close': list(stock_data.values_list('eod_price', flat=True)),
                    'movement_T1': DailyBinary.objects.get(ticker__ticker = entry, price_date = DailyBinary.objects.latest('price_date').price_date).movement_T1
                })
            else:
                top_stock_data.append({
                    'ticker': entry,
                    'company': TickerList.objects.get(ticker=entry).company_name,
                    'labels': list(map(self.date_to_str, list(stock_data.values_list('price_date', flat=True)))),
                    'data_close': list(stock_data.values_list('eod_price', flat=True)),
                    'movement_T1': 2
                })

        context['homepage_data'] = {
            # 'all_ticker':all_ticker,
            'top_ticker_list': combine_ticker_list,
            'display_feeds': display_feeds,
            'top_forecaster_list': top_forecaster_list,
            'labels': labels,
            'vnindex': data_close,
            'vnindex_movement': vnindex_movement,
            # 'top_followed_ticker': list(top_followed_ticker.keys()),
            # 'top_forecasted_ticker': list_top_forecasted_ticker,
            'top_stock_data': top_stock_data,
            'form':self.form_class
        } 

        return context


class TickerView(TemplateView):
    form_class = {'user_forecast': UserForecastForm, 'ticker_follow':TickerFollowForm, 'search_form':SearchForm}
    template_name = 'ticker.html'

    def next_day_calculator(self, current_day):
        if current_day.isoweekday() in set((5, 6, 7)):
            next_day = current_day + datetime.timedelta(days=(3 - current_day.isoweekday() % 5))
        else:
            next_day = current_day + datetime.timedelta(days=1)
        next_day = datetime.date(next_day.year, next_day.month, next_day.day)

        return next_day

    def next_4_day_calculator(self, next_day):
        if next_day.isoweekday() in set((4, 5, 6)):
            next_4_day = next_day + datetime.timedelta(5)
        else:
            next_4_day = next_day + datetime.timedelta(3)
        next_4_day = datetime.date(next_4_day.year, next_4_day.month, next_4_day.day)
        return next_4_day

    # def get_ticker_id(*args, **kwargs):
    #     ticker_id = kwargs['ticker'].upper()
    #     return ticker_id
    def get_date_variables(self):
        today = datetime.date.today()
        # T1 = self.next_day_calculator(current_day=today)
        # T3 = self.next_4_day_calculator(next_day=T1)
        if today.isoweekday() in set((1, 5)):
            cob = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=15, minute=0, second=0)
            forecast_cob = datetime.datetime(today.year, today.month, today.day, 12, 0, 0)
            if datetime.datetime.now() < cob:
                T1 = today
            else:
                T1 = self.next_day_calculator(current_day=today)
        else:
            last_day = today - datetime.timedelta(days=today.isoweekday() % 5)
            next_day = self.next_day_calculator(today)
            cob = datetime.datetime(year=last_day.year, month=last_day.month, day=last_day.day, hour=15, minute=0, second=0)
            forecast_cob = datetime.datetime(next_day.year, next_day.month, next_day.day, 12, 0, 0)
            T1 = self.next_day_calculator(current_day=today)
        
        T3 = self.next_4_day_calculator(next_day=T1)
        return T1, T3, cob, forecast_cob, today
    
    def get(self, request, *args, **kwargs):
       
        ticker_id = kwargs['ticker'].upper()
        
        ticker_obj = get_object_or_404(TickerList, ticker=ticker_id)
        utc = pytz.UTC
        tickerview_obj = TickerViewCount.objects.filter(ticker=ticker_obj, session=request.session.session_key)
        if tickerview_obj.exists() == False or (tickerview_obj.exists() and utc.localize(datetime.datetime.now()) >= (tickerview_obj.latest('created').created + datetime.timedelta(seconds=2))):
            if not request.session or not request.session.session_key:
                request.session.save()
            view = TickerViewCount(ticker=ticker_obj,
                                ip=request.META['REMOTE_ADDR'],
                                created=datetime.datetime.now(),
                                session=request.session.session_key,
                                user = request.user)
            view.save()
        
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        ticker_id = kwargs['ticker'].upper()

        if datetime.datetime.now() >= self.get_date_variables()[3]:
            form_forecast_date_T1 = self.get_date_variables()[0]
            form_forecast_date_T3 = self.get_date_variables()[1]
        else:
            if self.get_date_variables()[4].isoweekday() in set((6, 7)):
                form_forecast_date_T1 = self.get_date_variables()[0]
                form_forecast_date_T3 = self.get_date_variables()[1]
            else:
                form_forecast_date_T1 = self.get_date_variables()[4]
                form_forecast_date_T3 = self.next_4_day_calculator(next_day=form_forecast_date_T1)


        if request.method == "POST" and 'forecast' in request.POST:
            form = self.form_class['user_forecast'](request.POST or None)
            if form.is_valid():
                try:
                    obj = ForecastPrice.objects.get(
                        ticker = ticker_id, 
                        soier = request.user,
                        forecast_date_T1 = form_forecast_date_T1
                    )
                    if obj.updated_times < 3:
                        obj.forecast_movement_T1 = float(form.cleaned_data['forecast_movement_T1'])
                        obj.forecast_movement_T3 = float(form.cleaned_data['forecast_movement_T3'])
                        obj.save()
                except:
                    ForecastPrice.objects.create(
                        ticker = TickerList.objects.get(ticker = ticker_id), 
                        soier = request.user,
                        forecast_movement_T1 = float(form.cleaned_data['forecast_movement_T1']), 
                        forecast_movement_T3 = float(form.cleaned_data['forecast_movement_T3']),
                        forecast_date_T1 = form_forecast_date_T1,
                        forecast_date_T3 = form_forecast_date_T3,
                    )
            context = self.get_context_data(*args, **kwargs)
            return redirect('tickerview', ticker = ticker_id)

        if request.method == 'POST' and 'follow' in request.POST:
            follow_form = self.form_class['ticker_follow'](request.POST or None)
            if follow_form.is_valid():
                try:
                    TickerFollowing.objects.create(ticker_id = TickerList.objects.get(ticker = ticker_id), follower_id = request.user)
                except IntegrityError:
                    obj = TickerFollowing.objects.get(ticker_id = TickerList.objects.get(ticker = ticker_id), follower_id = request.user)
                    obj.delete()
            context = self.get_context_data(*args, **kwargs)
            return self.render_to_response(context=context)

        if request.method == 'POST' and 'ticker_id' in request.POST:
            search_form = self.form_class['search_form'](request.POST or None)
            if search_form.is_valid():
                ticker_search = search_form.cleaned_data['ticker_id']

            return redirect('tickerview', ticker_search)

    def date_to_str(self, price_date):
        return price_date.strftime("%d/%m/%Y")

    def get_top_forecaster(self,  ticker_id, forecast_date): #come back for calculation performance logic
        if ForecastPrice.objects.filter(ticker = ticker_id, forecast_date_T1 = forecast_date).exists():
            soier_exist = 1
            forecaster_list = list(ForecastPrice.objects.filter(ticker = ticker_id, forecast_date_T1 = forecast_date).values_list('soier__username', 'forecast_movement_T1', 'forecast_movement_T3'))
            
            forecaster_rank = sorted([{'name': forecaster[0], 'forecast_T1': forecaster[1], 'forecast_T3': forecaster[2], 'pfm': UserProfile.objects.get(user__username = forecaster[0]).pfm_all[0]} for forecaster in forecaster_list], key=lambda d: d['pfm'], reverse=True)
        else:
            soier_exist = 0
            forecaster_rank = 'Chưa có ai tham gia dự báo'
        return soier_exist, forecaster_rank

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        ticker_id = kwargs['ticker'].upper()
       
        stock_data = StockDb.objects.filter(ticker=ticker_id).order_by('price_date')
        company_name = TickerList.objects.get(ticker=ticker_id).company_name
        if DailyBinary.objects.filter(ticker=ticker_id).filter(price_date = DailyBinary.objects.latest('price_date').price_date).exists():
            movement = DailyBinary.objects.get(ticker=ticker_id, price_date = DailyBinary.objects.latest('price_date').price_date).movement_T1
        else:
            movement = 2
        labels = list(map(self.date_to_str, list(stock_data.values_list('price_date', flat=True))))
        data_close = list(stock_data.values_list('eod_price', flat=True))
        volumn = list(stock_data.values_list('volumn', flat=True))

        #aggregate ticker view by date
        viewcount = TickerViewCount.objects.filter(ticker=ticker_id)
        total_viewcount = viewcount.count()
        daily_viewcount = viewcount.extra({'created_date':"date(created)"}).values('created_date').annotate(created_count = Count('ticker')).order_by('created_date')
        viewcount_labels = list(map(self.date_to_str, list(daily_viewcount.values_list('created_date', flat=True))))
        viewcount_data = list(daily_viewcount.values_list('created_count', flat=True))

        forecast_date_T1 = datetime.datetime.today()
        forecast_date_T3 = datetime.datetime.today()
        forecast_T1 = 0
        forecast_T3 = 0
        forecast_movement_T1 = 0
        forecast_movement_T3 = 0
        __forecast_movement_T1 = 0
        __forecast_movement_T3 = 0
        total_forecast = 0
        recommend = "NA"

        if ForecastPrice.objects.filter(ticker=ticker_id, soier__username = "AI").exists():
            forecast_qs = ForecastPrice.objects.filter(ticker=ticker_id)
            total_forecast = forecast_qs.count()
            forecast_data = forecast_qs.filter(soier__username = "AI").latest('forecast_date_T1')
            if datetime.datetime.now() >= self.get_date_variables()[2]:
                if forecast_data.forecast_date_T1 == self.get_date_variables()[0]:
                    check_exist = 1
                    forecast_date_T1 = forecast_data.forecast_date_T1
                    forecast_date_T3 = forecast_data.forecast_date_T3
                    forecast_T1 = forecast_data.forecast_eod_T1
                    forecast_T3 = forecast_data.forecast_eod_T3
                    forecast_movement_T1 = forecast_data.forecast_movement_T1
                    forecast_movement_T3 = forecast_data.forecast_movement_T3
                    if forecast_movement_T1 == 1:
                        __forecast_movement_T1 = "Tăng"
                    elif forecast_movement_T1 == -1:
                        __forecast_movement_T1 = "Giảm"
                    elif forecast_movement_T1 == 0:
                        __forecast_movement_T1 = "Ngang"

                    if forecast_movement_T3 == 1:
                        __forecast_movement_T3 = "Tăng"
                    elif forecast_movement_T3 == -1:
                        __forecast_movement_T3 = "Giảm"
                    elif forecast_movement_T3 == 0:
                        __forecast_movement_T3 = "Ngang"    
                    # need to come back for recommendation logic
                    if forecast_movement_T1 == 1:
                        if forecast_movement_T3 == 1:
                            recommend = 'Kịch bản 1'
                        elif forecast_movement_T3 == -1:
                            recommend = 'Kịch bản 2'
                        elif forecast_movement_T3 == 0:
                            recommend = 'Kịch bản 3'
                    elif forecast_movement_T1 == -1:
                        if forecast_movement_T3 == 1:
                            recommend = 'Kịch bản 4'
                        elif forecast_movement_T3 == -1:
                            recommend = 'Kịch bản 5'
                        elif forecast_movement_T3 == 0:
                            recommend = 'Kịch bản 6'
                    elif forecast_movement_T1 == 0:
                        if forecast_movement_T3 == 1:
                            recommend = 'Kịch bản 7'
                        elif forecast_movement_T3 == -1:
                            recommend = 'Kịch bản 8'
                        elif forecast_movement_T3 == 0:
                            recommend = 'Kịch bản 9'
                else:
                    check_exist = 0
            else:
                if forecast_data.forecast_date_T1 == self.get_date_variables()[4]:
                    check_exist = 1
                    forecast_date_T1 = forecast_data.forecast_date_T1
                    forecast_date_T3 = forecast_data.forecast_date_T3
                    forecast_T1 = forecast_data.forecast_eod_T1
                    forecast_T3 = forecast_data.forecast_eod_T3
                    forecast_movement_T1 = __forecast_movement_T1
                    forecast_movement_T3 = __forecast_movement_T3
                    if forecast_movement_T1 == 1:
                        __forecast_movement_T1 = "Tăng"
                    elif forecast_movement_T1 == -1:
                        __forecast_movement_T1 = "Giảm"
                    elif forecast_movement_T1 == 0:
                        __forecast_movement_T1 = "Ngang"

                    if forecast_movement_T3 == 1:
                        __forecast_movement_T3 = "Tăng"
                    elif forecast_movement_T3 == -1:
                        __forecast_movement_T3 = "Giảm"
                    elif forecast_movement_T3 == 0:
                        __forecast_movement_T3 = "Ngang"   
                    # need to come back for recommendation logic
                    if forecast_movement_T1 == 1:
                        if forecast_movement_T3 == 1:
                            recommend = 'Kịch bản 1'
                        elif forecast_movement_T3 == -1:
                            recommend = 'Kịch bản 2'
                        elif forecast_movement_T3 == 0:
                            recommend = 'Kịch bản 3'
                    elif forecast_movement_T1 == -1:
                        if forecast_movement_T3 == 1:
                            recommend = 'Kịch bản 4'
                        elif forecast_movement_T3 == -1:
                            recommend = 'Kịch bản 5'
                        elif forecast_movement_T3 == 0:
                            recommend = 'Kịch bản 6'
                    elif forecast_movement_T1 == 0:
                        if forecast_movement_T3 == 1:
                            recommend = 'Kịch bản 7'
                        elif forecast_movement_T3 == -1:
                            recommend = 'Kịch bản 8'
                        elif forecast_movement_T3 == 0:
                            recommend = 'Kịch bản 9'
                else:
                    check_exist = 0
        else:
            check_exist = 0

        form_forecast_date_T1 = self.get_date_variables()[0]
        form_forecast_date_T3 = self.get_date_variables()[1]
       
        try:

            obj = ForecastPrice.objects.get(
                ticker = ticker_id, 
                soier = self.request.user,
                forecast_date_T1 = form_forecast_date_T1
            )
            updated_count = 3 - obj.updated_times
        except:
            updated_count = 3

        #display rss feed
        ticker_feeds = feedparser.parse('https://www.stockbiz.vn/RSS/News/Company.ashx')
        title_link_1 = [{'title': entry.title, 'link': entry.link} for entry in ticker_feeds.entries]
        main_feeds = [sub for sub in title_link_1 if sub['title'].find(ticker_id) >= 0]

        market_feeds = feedparser.parse('https://www.stockbiz.vn/RSS/News/TopStories.ashx')
        title_link_2 = [{'title': entry.title, 'link': entry.link} for entry in market_feeds.entries]
        if len(title_link_2) > 10:
            other_feeds = random.sample(title_link_2, 20)
        else:
            other_feeds = title_link_2[0:len(title_link_2)]

        display_feeds = main_feeds + other_feeds

        #top forecaster
        __get_top_forecaster = self.get_top_forecaster(ticker_id=ticker_id, forecast_date=form_forecast_date_T1)
        top_forecaster = __get_top_forecaster[1]
        soier_exist = __get_top_forecaster[0]

        if self.request.user.is_authenticated:
            if TickerFollowing.objects.filter(ticker_id = TickerList.objects.get(ticker = ticker_id), follower_id = self.request.user).exists():
                ticker_followed_status = 1
            else:
                ticker_followed_status = 0
        else:
            ticker_followed_status = 2

        context['stock_data'] = {
            'ticker': ticker_id,
            'company_name': company_name,
            'labels': labels,
            'data_close': data_close,
            'volumn': volumn,
            'movement': movement,
            'total_forecast': total_forecast,
            'total_viewcount': total_viewcount,
            'viewcount_labels': viewcount_labels,
            'viewcount_data': viewcount_data,
            'display_feeds': display_feeds,
            'ticker_followed_status': ticker_followed_status
            }

        context['forecast_data'] = {
            'check_exist': check_exist,
            'forecast_date_T1': forecast_date_T1,
            'forecast_date_T3': forecast_date_T3,
            'forecast_T1': forecast_T1,
            'forecast_T3': forecast_T3,
            'forecast_movement_T1': forecast_movement_T1,
            'forecast_movement_T3': forecast_movement_T3,
            'strforecast_movement_T1': __forecast_movement_T1,
            'strforecast_movement_T3': __forecast_movement_T3,
            'recommend': recommend,
            'soier_exist': soier_exist,
            'top_forecaster': top_forecaster,
        }

        context['form_data'] = {
            'form': UserForecastForm,
            'search_form': SearchForm,
            'form_forecast_date_T1': form_forecast_date_T1,
            'form_forecast_date_T3': form_forecast_date_T3,
            'updated_count': updated_count
        }
        return context

class UserView(TemplateView):
    form_class = {'follower_form': FollowerForm, 'search_form':SearchForm}
    template_name = 'user_view.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.username == kwargs['username']:
            return redirect('profileview')
        else:
            return super(UserView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        if request.method == 'POST' and 'userfollow' in request.POST:
            form = self.form_class['follower_form'](request.POST or None)
            if form.is_valid():
                try:
                    UserFollowing.objects.create(user_id = User.objects.get(username = kwargs['username']), follower_id = request.user)
                except IntegrityError:
                    obj = UserFollowing.objects.get(user_id = User.objects.get(username = kwargs['username']), follower_id = request.user)
                    obj.delete()
        
            context = self.get_context_data(*args, **kwargs)
            return redirect('userview', username = kwargs['username'])

        if request.method == 'POST' and 'ticker_id' in request.POST:
            search_form = self.form_class['search_form'](request.POST or None)
            if search_form.is_valid():
                ticker_search = search_form.cleaned_data['ticker_id']

            return redirect('tickerview', ticker_search)

        
        
    def get_context_data(self, *args, **kwargs):
        username = kwargs['username']
        context = super().get_context_data(**kwargs)

        get_user = get_object_or_404(User, username = username)
        get_user_profile = get_object_or_404(UserProfile, user = get_user)

        if self.request.user.is_authenticated:
            if UserFollowing.objects.filter(user_id = User.objects.get(username = kwargs['username']), follower_id = self.request.user).exists():
                followed_status = 1
            else:
                followed_status = 0
        else:
            followed_status = 3

            #revisit for logic for anonymous user
        
        display_name = get_user_profile.display_name
        join_date = get_user_profile.created.strftime("%d/%m/%Y")
        reputation_point = get_user_profile.reputation
        forecast_no = ForecastPrice.objects.filter(soier = get_user).count()
        follower_no = UserFollowing.objects.filter(user_id = get_user).count()

        if get_user_profile.avatar:
            has_avatar = 1
            avatar = get_user_profile.avatar
        else:
            has_avatar = 0
        
        if get_user_profile.bio != '':
            bio = get_user_profile.bio
        else:
            bio = 'Chưa có nội dung giới thiệu'

        follower_list_qs = list(UserFollowing.objects.filter(user_id = get_user).values_list('follower_id', flat=True))
        if len(follower_list_qs) > 0:
            has_follower = 1
            follower_list = [User.objects.get(id = follower).username for follower in follower_list_qs]
        else:
            has_follower = 0
            follower_list = get_user.username + ' chưa có người follow'

        following_list_qs = list(UserFollowing.objects.filter(follower_id = get_user).values_list('user_id', flat=True))
        if len(following_list_qs) > 0:
            has_following = 1
            following_list = [User.objects.get(id = following).username for following in following_list_qs]
        else:
            has_following = 0
            following_list = get_user.username + ' chưa follow ai'

        ticker_follow_qs = list(TickerFollowing.objects.filter(follower_id = get_user).values_list('ticker_id', flat=True))
        if len(ticker_follow_qs) > 0:
            following_ticker = 1
            ticker_follow_list = [TickerList.objects.get(ticker = ticker_id) for ticker_id in ticker_follow_qs]
        else:
            following_ticker = 0
            ticker_follow_list = get_user.username + ' không theo dõi mã cổ phiếu nào'

        recent_date = datetime.datetime.today() - datetime.timedelta(10)
        recent_date = pytz.timezone('utc').localize(recent_date)
        recent_view_qs = TickerViewCount.objects.filter(user = get_user.username).filter(created__gte = recent_date)

        if recent_view_qs.count() > 0:
            has_view = 1
            recent_view_list = list(recent_view_qs.values('ticker').distinct().values_list('ticker', flat=True))
        else:
            has_view = 0
            recent_view_list = 'Không có hoạt động gần đây'
            #revisit for aggregate movement into the recent_view

        get_date_variables = TickerView().get_date_variables()
        user_forecast_qs = list(ForecastPrice.objects.filter(soier = get_user).filter(forecast_date_T1 = get_date_variables[0]).values_list('ticker', 'forecast_movement_T1', 'forecast_movement_T3'))
        forecast_date_T1 = get_date_variables[0].strftime('%d/%m/%Y')
        forecast_date_T3 = get_date_variables[1].strftime('%d/%m/%Y')
        if len(user_forecast_qs) > 0:
            user_forecast_list = [{'ticker': forecast[0], 'company_name': TickerList.objects.get(ticker=forecast[0]).company_name,'forecast_movement_T1': forecast[1],'forecast_movement_T3': forecast[2]} for forecast in user_forecast_qs]
            has_forecast = 1
        else:
            user_forecast_list = get_user.username + ' chưa đưa dự báo cho ngày ' + get_date_variables[0].strftime('%d/%m/%Y')
            has_forecast = 0

        context['follow_status'] = followed_status

        context['general_info'] = {
            'display_name': display_name,
            'has_avatar':has_avatar,
            'avatar': avatar,
            'join_date': join_date,
            'reputation_point': reputation_point,
            'forecast_number': forecast_no,
            'follower_no': follower_no,
            'bio': bio,
            'has_follower': has_follower,
            'follower_list': follower_list,
            'has_following': has_following,
            'following_list': following_list,
            'has_view': has_view,
            'recent_view_list': recent_view_list,
            'following_ticker': following_ticker,
            'ticker_follow_list': ticker_follow_list,
            'has_forecast': has_forecast,
            'user_forecast_list': user_forecast_list,
            'forecast_date_T1': forecast_date_T1,
            'forecast_date_T3': forecast_date_T3,
        }

        context['form_data'] = {
            'search_form': SearchForm
        }

        return context

class ProfileView(TemplateView):
    form_class = {'ticker_unfollow_form': TickerUnfollow, 'search_form': SearchForm}
    template_name = 'profile_view.html'

    def post(self, request, *args, **kwargs):

        if request.method == 'POST' and 'tickerunfollow' in request.POST:
            form_unfollow = self.form_class['ticker_unfollow_form'](request.POST or None)
            if form_unfollow.is_valid():
                try:
                    obj = TickerFollowing.objects.get(ticker_id = TickerList.objects.get(ticker = request.POST['ticker_unfollow_id']))
                    obj.delete()
                except:
                    pass
        
            return redirect('profileview')

        if request.method == 'POST' and 'ticker_id' in request.POST:
            search_form = self.form_class['search_form'](request.POST or None)
            if search_form.is_valid():
                ticker_search = search_form.cleaned_data['ticker_id']

            return redirect('tickerview', ticker_search)
        
    def get_context_data(self, *args, **kwargs):
        username = self.request.user.username
        context = super().get_context_data(**kwargs)

        get_user = get_object_or_404(User, username = username)
        get_user_profile = get_object_or_404(UserProfile, user = get_user)

            #revisit for logic for anonymous user

        display_name = get_user_profile.display_name
        join_date = get_user_profile.created.strftime("%d/%m/%Y")
        reputation_point = get_user_profile.reputation
        forecast_no = ForecastPrice.objects.filter(soier = get_user).count()
        follower_no = UserFollowing.objects.filter(user_id = get_user).count()

        if get_user_profile.avatar:
            has_avatar = 1
            avatar = get_user_profile.avatar
        else:
            has_avatar = 0
        
        if get_user_profile.bio != '':
            bio = get_user_profile.bio
        else:
            bio = 'Bạn chưa có nội dung giới thiệu'

        follower_list_qs = list(UserFollowing.objects.filter(user_id = get_user).values_list('follower_id', flat=True))
        if len(follower_list_qs) > 0:
            has_follower = 1
            follower_list = [User.objects.get(id = follower).username for follower in follower_list_qs]
        else:
            has_follower = 0
            follower_list = 'Bạn chưa có người follow'

        following_list_qs = list(UserFollowing.objects.filter(follower_id = get_user).values_list('user_id', flat=True))
        if len(following_list_qs) > 0:
            has_following = 1
            following_list = [User.objects.get(id = following).username for following in following_list_qs]
        else:
            has_following = 0
            following_list = 'Bạn chưa follow ai'

        ticker_follow_qs = list(TickerFollowing.objects.filter(follower_id = get_user).values_list('ticker_id', flat=True))
        if len(ticker_follow_qs) > 0:
            following_ticker = 1
            ticker_follow_list = [TickerList.objects.get(ticker = ticker_id) for ticker_id in ticker_follow_qs]
        else:
            following_ticker = 0
            ticker_follow_list = 'Bạn không theo dõi mã cổ phiếu nào'

        recent_date = datetime.datetime.today() - datetime.timedelta(10)
        recent_date = pytz.timezone('utc').localize(recent_date)
        recent_view_qs = TickerViewCount.objects.filter(user = get_user.username).filter(created__gte = recent_date)

        if recent_view_qs.count() > 0:
            has_view = 1
            recent_view_list = list(recent_view_qs.values('ticker').distinct().values_list('ticker', flat=True))
        else:
            has_view = 0
            recent_view_list = 'Bạn không xem cổ phiếu nào gần đây'
            #revisit for aggregate movement into the recent_view

        get_date_variables = TickerView().get_date_variables()
        user_forecast_qs = list(ForecastPrice.objects.filter(soier = get_user).filter(forecast_date_T1 = get_date_variables[0]).values_list('ticker', 'forecast_movement_T1', 'forecast_movement_T3'))
        forecast_date_T1 = get_date_variables[0].strftime('%d/%m/%Y')
        forecast_date_T3 = get_date_variables[1].strftime('%d/%m/%Y')
        if len(user_forecast_qs) > 0:
            user_forecast_list = [{'ticker': forecast[0], 'company_name': TickerList.objects.get(ticker=forecast[0]).company_name,'forecast_movement_T1': forecast[1],'forecast_movement_T3': forecast[2]} for forecast in user_forecast_qs]
            has_forecast = 1
        else:
            user_forecast_list = 'Bạn chưa đưa dự báo cho ngày ' + get_date_variables[0].strftime('%d/%m/%Y')
            has_forecast = 0

        # context['follow_status'] = followed_status

        context['general_info'] = {
            'display_name': display_name,
            'username': get_user.username,
            'has_avatar':has_avatar,
            'avatar': avatar,
            'join_date': join_date,
            'reputation_point': reputation_point,
            'forecast_number': forecast_no,
            'follower_no': follower_no,
            'bio': bio,
            'has_follower': has_follower,
            'follower_list': follower_list,
            'has_following': has_following,
            'following_list': following_list,
            'has_view': has_view,
            'recent_view_list': recent_view_list,
            'following_ticker': following_ticker,
            'ticker_follow_list': ticker_follow_list,
            'has_forecast': has_forecast,
            'user_forecast_list': user_forecast_list,
            'forecast_date_T1': forecast_date_T1,
            'forecast_date_T3': forecast_date_T3
            
        }

        context['form_unfollow'] = self.form_class['ticker_unfollow_form']

        context['form_data'] = {
            'search_form': SearchForm
        }

        return context

class ProfileEditView(LoginRequiredMixin ,TemplateView):
    form_class = {'profile_edit_form': ProfileEditForm, 'search_form':SearchForm}
    template_name = 'edit_profile.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login')
        else:
            return super(ProfileEditView, self).dispatch(request, *args, **kwargs)

    
    def get_object(self):
        obj = UserProfile.objects.get(user = self.request.user)
        return obj

    def post(self, request, *args, **kwargs):
        if request.method == "POST" and 'ticker_id' not in request.POST:
            form = self.form_class['profile_edit_form'](request.POST or None, request.FILES, instance=self.get_object())
            if form.is_valid():
                if self.get_object().avatar.name != 'user.png' and self.get_object().avatar.name != form.cleaned_data['avatar']:
                    self.get_object().avatar.delete()
                else:
                    pass
                form.save()

        if request.method == 'POST' and 'ticker_id' in request.POST:
            search_form = self.form_class['search_form'](request.POST or None)
            if search_form.is_valid():
                ticker_search = search_form.cleaned_data['ticker_id']

            return redirect('tickerview', ticker_search)


        context = self.get_context_data(*args, **kwargs)
        return redirect('profileview')


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        
        get_user = get_object_or_404(User, username = self.request.user.username)
        get_user_profile = get_object_or_404(UserProfile, user = get_user)

        display_name = get_user_profile.display_name

        if get_user_profile.avatar:
            has_avatar = 1
            avatar = get_user_profile.avatar
        else:
            has_avatar = 0
            avatar = 'user.png'

        join_date = get_user_profile.created.strftime("%d/%m/%Y")
        reputation_point = get_user_profile.reputation
        forecast_no = ForecastPrice.objects.filter(soier = get_user).count()
        follower_no = UserFollowing.objects.filter(user_id = get_user).count()

        context['profile_form'] = self.form_class['profile_edit_form'](instance=self.get_object())

        context['general_info'] = {
            'username': get_user_profile.user.username,
            'has_avatar':has_avatar,
            'avatar':avatar,
            'display_name': display_name,
            'join_date': join_date,
            'reputation_point': reputation_point,
            'forecast_number': forecast_no,
            'follower_no': follower_no,
        }

        context['form_data'] = {
            'search_form': SearchForm
        }

        return context



    

        







