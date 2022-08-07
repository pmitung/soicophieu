from django.urls import path

from .views import ProfileEditView, ProfileView, TickerView, UserView, HomePageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('ticker/<str:ticker>', TickerView.as_view(), name='tickerview'),
    path('user/<str:username>', UserView.as_view(), name='userview'),
    path('accounts/profile/', ProfileView.as_view(), name='profileview'),
    path('accounts/profile/edit', ProfileEditView.as_view(), name='editprofile'),
  
]