from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'^ticker/(?P<ticker_id>[\w.@+-]+)', consumers.ChartConsumer.as_asgi()),
]