from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter

class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        print(request.META)
        path = "/accounts/profile/"
        return path

    def get_logout_redirect_url(self, request):
        path = "/"
        return path

    
