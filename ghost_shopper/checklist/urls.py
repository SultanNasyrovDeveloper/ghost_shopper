from django.urls import include, path

from . import views

app_name = 'checklist'


urlpatterns = [
    path('constructor/', include('ghost_shopper.checklist.constructor.urls', namespace='constructor')),
    path('<int:pk>', views.ChecklistDetailView.as_view(), name='detail'),
    path('<int:pk>/update', views.ChecklistUpdateView.as_view(), name='update'),
    path('<int:pk>/appeal', views.ChecklistAppealView.as_view(), name='appeal'),
    path('<int:pk>/audio', views.get_checklist_audio, name='audio'),
    path('image/delete', views.delete_image, name='delete-image'),
]
