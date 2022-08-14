import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import forecast.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soicophieu.settings")

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            forecast.routing.websocket_urlpatterns
        )
    ),
})