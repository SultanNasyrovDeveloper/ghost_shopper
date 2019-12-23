from django.urls import path
from . import views


app_name = 'chat'


urlpatterns = [
    path('<int:pk>/create-message', views.MessageCreateView.as_view(), name='create-message'),
    path('<int:pk>/delete-message', views.delete_message, name='delete-message'),
    path('create-comment', views.create_comment, name='create-comment'),
    path('<int:pk>/delete-comment', views.delete_comment, name='delete-comment')
]