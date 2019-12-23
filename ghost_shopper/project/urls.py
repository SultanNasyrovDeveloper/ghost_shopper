from django.urls import path

from . import views


app_name = 'project'


urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path('create/', views.ProjectCreateView.as_view(), name='create'),
    path('<int:pk>', views.ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/update', views.ProjectUpdateView.as_view(), name='update'),
    path('<int:pk>/multiply', views.ProjectChecksMultiplyView.as_view(), name='multiply'),
    path('<int:pk>/delete', views.ProjectDeleteView.as_view(), name='delete'),

    path('autocomplete', views.ProjectNameAutocomplete.as_view(), name='autocomplete'),
]
