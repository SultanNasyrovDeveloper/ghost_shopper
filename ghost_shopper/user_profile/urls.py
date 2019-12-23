from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from . import forms


app_name = 'profile'


urlpatterns = [
    path('', views.UserListView.as_view(), name='list'),
    path('performers/', views.PerformerListView.as_view(), name='performers'),

    path('create/staff', views.UserCreateView.as_view(form_class=forms.StaffCreationForm), name='create-staff'),
    path('create/performer', views.UserCreateView.as_view(form_class=forms.PerformerCreationForm), name='create-performer'),

    path('<int:pk>', views.UserProfileDetail.as_view(), name='detail'),
    path('<int:pk>/update', views.ProfileUpdateView.as_view(), name='update'),
    path('<int:pk>/permissions', views.UserPermissionsUpdate.as_view(), name='permissions-update'),
    path('<int:pk>/delete', views.UserDeleteView.as_view(), name='delete'),

    path('auto/<int:pk>/delete', views.PerformerAutoDeleteView.as_view(), name='delete-auto'),

    path('approve-request', views.PerformerApprovalRequestListView.as_view(), name='approval-request-list'),
    path('<int:pk>/approval-request/create',
         views.PerformerApprovalRequestCreateView.as_view(),
         name='approval_request'),
    path('<int:pk>/approval-request/accept',
         views.PerformerApprovalRequestAcceptView.as_view(),
         name='approval-request-accept'),
    path('<int:pk>/approval-request/decline',
         views.PerformerApprovalRequestDeclineView.as_view(),
         name='approval-request-decline'),

    path('autocomplete', views.UserAutocompleteView.as_view(), name='autocomplete'),
    path('autocomplete/performer', views.PerformerAutocompleteView.as_view(), name='performer-autocomplete'),
    path('autocomplete/car-brand', views.PerformerCarBrandAutocompleteView.as_view(), name='car-brand-autocomplete'),
    path('autocomplete/car-model', views.PerformerCarModelAutocompleteView.as_view(), name='car-model-autocomplete')

]