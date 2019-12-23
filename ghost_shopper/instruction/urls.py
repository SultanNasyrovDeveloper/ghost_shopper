from django.urls import path

from . import views


app_name = 'instruction'


urlpatterns = [
    path('', views.InstructionListView.as_view(), name='list'),
    path('create', views.InstructionCreateView.as_view(), name='create'),
    path('<int:pk>', views.InstructionDetailView.as_view(), name='detail'),
    path('<int:pk>/update', views.InstructionUpdateView.as_view(), name='update'),
    path('<int:pk>/delete', views.InstructionDeleteView.as_view(), name='delete'),

    path('autocomplete', views.InstructionAutocompleteView.as_view(), name='autocomplete'),
    path('autocomplete/search', views.InstructionSearchAutocompleteView.as_view(), name='search-autocomplete'),
]