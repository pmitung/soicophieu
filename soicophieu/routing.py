# from django.urls import re_path
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

# import forecast.routing

# application = ProtocolTypeRouter({
#     'websocket': AllowedHostsOriginValidator(
#         AuthMiddlewareStack(
#             URLRouter(
#                 [
#                     forecast.routing.websocket_urlpatterns
#                 ]
#             )
#         )
#     )
# })