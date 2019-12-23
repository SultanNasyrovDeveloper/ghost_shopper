from django.urls import path
from . import views


app_name = 'index_page'


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('index/settings', views.IndexPageUpdateView.as_view(), name='update'),
]