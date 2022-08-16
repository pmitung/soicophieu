from django.conf import settings
from django.apps import apps
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin, ImportExportMixin
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget
from import_export.fields import Field
from django import forms
# from forecast.models import Comment, ForecastPrice, TickerFollowing, StockDb, TickerViewCount, UserFollowing, UserPerformance, UserProfile

User = settings.AUTH_USER_MODEL

class CsvImportForm(forms.Form):
    csv_file =  forms.FileField()

class StockDbResource(resources.ModelResource):
    from .models import TickerList
    def before_save_instance(self, instance, using_transactions, dry_run):
        instance.dry_run = dry_run # set a temporal flag for dry-run mode
    
    ticker = fields.Field(
        column_name='ticker',
        attribute='ticker',
        widget=ForeignKeyWidget(TickerList, 'ticker')
    )

    class Meta:
        from .models import StockDb
        model = StockDb
        fields = ('id', 'ticker', 'price_date', 'open_price', 'high_price', 'low_price', 'eod_price', 'volumn')
        import_id_fields = ['id',]
        widgets = {
            'price_date': {'format': '%Y%m%d'}
        }

class TickerListResource(resources.ModelResource):
    class Meta:
        from .models import TickerList
        model = TickerList
        fields = ('id', 'company_id', 'ticker', 'code_id', 'ex', 'company_name')
        import_id_fields = ['id',]

class DailyBinaryResources(resources.ModelResource):
    from .models import TickerList
    ticker = fields.Field(
            column_name='ticker',
            attribute='ticker',
            widget=ForeignKeyWidget(TickerList, 'ticker')
        )

    class Meta:
        from .models import DailyBinary
        model = DailyBinary
        fields = ('id', 'ticker', 'price_date', 'movement_T1', 'movement_T3')
        import_id_fields = ['id',]
        widgets = {
            'price_date': {'format': '%Y%m%d'}
        }

class ForecastPriceResources(resources.ModelResource):
    from .models import TickerList
    soier = fields.Field(
        column_name = 'soier',
        attribute = 'soier',
        widget = ForeignKeyWidget(User, 'username')
    )

    ticker = fields.Field(
        column_name='ticker',
        attribute='ticker',
        widget=ForeignKeyWidget(TickerList, 'ticker')
    )

    class Meta:
        from .models import ForecastPrice
        model = ForecastPrice
        fields = ('id', 'ticker', 'soier', 'forecast_eod_T1', 'forecast_eod_T3', 'forecast_movement_T1', 'forecast_movement_T3', 'forecast_date_T1', 'forecast_date_T3',)
        # exclude = ('id',)
        import_id_fields = ['id',]
        widgets = {
            'forecast_date_T1': {'format': '%Y%m%d'},
            'forecast_date_T3': {'format': '%Y%m%d'}
        }

class UserPerformanceResources(resources.ModelResource):
    from .models import TickerList
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget= ForeignKeyWidget(User, 'username')
    )

    ticker = fields.Field(
        column_name= 'ticker',
        attribute= 'ticker',
        widget= ForeignKeyWidget(TickerList, 'ticker')
    )

    class Meta:
        from .models import UserPerformance
        model = UserPerformance
        fields = ('id', 'user', 'ticker', 'evaluation_date', 'performance_T1', 'performance_T3')
        import_id_fields = ['id',]
        widgets = {
            'evaluation_date': {'format': '%Y%m%d'},
        }

from .models import TickerList
@admin.register(TickerList)
class TickerListAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('ticker', 'company_name')
    search_fields = ('ticker',)
    resource_class = TickerListResource

from .models import StockDb
@admin.register(StockDb)
class StockDbAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('get_ticker', 'price_date', 'open_price', 'eod_price', 'high_price', 'low_price')
    search_fields = ('ticker__ticker',)
    resource_class = StockDbResource

    def get_ticker(self, obj):
        return obj.ticker.ticker

from .models import DailyBinary
@admin.register(DailyBinary)
class DailyBinaryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('get_ticker', 'price_date', 'movement_T1', 'movement_T3')
    search_fields = ('ticker__ticker',)
    resource_class = DailyBinaryResources

    def get_ticker(self, obj):
        return obj.ticker.ticker

from .models import UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_useremail', 'reputation', 'pfm_all','created')
    search_fields = ('user__username',)

    def get_username(self, obj):
        return obj.user.username

    def get_useremail(self, obj):
        return obj.user.email

from .models import ForecastPrice
@admin.register(ForecastPrice)
class ForecastPriceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('get_username', 'get_ticker', 'forecast_eod_T1', 'forecast_movement_T1', 'forecast_date_T1', 'forecast_eod_T3', 'forecast_movement_T3', 'forecast_date_T3', 'created_at', 'updated_times')
    search_fields = ('ticker__ticker','soier__username')
    list_filter = ('forecast_date_T1', 'forecast_date_T3')
    resource_class = ForecastPriceResources
    
    def get_username(self, obj):
        return obj.soier.username

    def get_ticker(self, obj):
        return obj.ticker.ticker

from .models import UserPerformance
@admin.register(UserPerformance)
class UserPerformanceAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_ticker', 'evaluation_date', 'performance_T1', 'performance_T3')

    def get_username(self, obj):
        return obj.user.username

    def get_ticker(self, obj):
        return obj.ticker.ticker

    def performance_T1(self, obj):
        if obj.performance_T1:
            return True
        else:
            return False

    def performance_T3(self, obj):
        if obj.performance_T3:
            return True
        else:
            return False

from .models import Comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_ticker', 'content', 'comment_time')

    def get_username(self, obj):
        return obj.soier.username

    def get_ticker(self, obj):
        return obj.ticker.ticker

from .models import TickerViewCount
@admin.register(TickerViewCount)
class TickerViewAdmin(admin.ModelAdmin):
    list_display = ('get_ticker', 'ip', 'session', 'created', 'user')

    def get_ticker(self, obj):
        return obj.ticker.ticker

from .models import UserFollowing
@admin.register(UserFollowing)
class UserFollowingAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'follower_id')

from .models import TickerFollowing
@admin.register(TickerFollowing)
class TickerFollowingAdmin(admin.ModelAdmin):
    list_display = ('ticker_id', 'follower_id')