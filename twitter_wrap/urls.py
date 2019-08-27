from django.urls import path, re_path
from .views import WrapperView, delete_cache, check_cache


app_name = 'twitter_wrap'
urlpatterns = [
    path('cache_clear', delete_cache),
    #path('cache_check', check_cache),
    re_path('(?P<path>.*)', WrapperView.as_view()),
]
