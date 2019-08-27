from django.urls import path

from . import views


app_name = 'twitter_login'
urlpatterns = [
    path('', views.get_authenticate_url_view, name='get_url'),
    path('callback', views.callback_routing, name='callback'),
    path('logined', views.logined, name='logined'),
    path('logout', views.logout, name='logout'),
]
