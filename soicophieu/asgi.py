# import os

# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.core.asgi import get_asgi_application
# import forecast.routing

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soicophieu.settings")

# django_asgi_app = get_asgi_application()

# application = ProtocolTypeRouter({
#   "https": django_asgi_app,
#   "websocket": AuthMiddlewareStack(
#         URLRouter(
#             forecast.routing.websocket_urlpatterns
#         )
#     ),
# })