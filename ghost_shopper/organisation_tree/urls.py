from django.urls import path
from . import views


app_name = 'organisation'


urlpatterns = [
    path('', views.OrganisationListView.as_view(), name='list'),
    path('create', views.OrganisationCreateView.as_view(), name='create'),
    path('<int:pk>', views.OrganisationDetailView.as_view(), name='detail'),
    path('<int:pk>/update', views.OrganisationUpdateView.as_view(), name='update'),
    path('<int:pk>/delete', views.OrganisationDeleteView.as_view(), name='delete'),
    path('<int:pk>/statistics', views.OrganisationStatisticsView.as_view(), name='statistics'),

    path('<int:pk>/create/employee', views.CreateEmployeeView.as_view(), name='create-employee'),

    path('<int:pk>/docs', views.OrganisationDocsListView.as_view(), name='docs'),
    path('docs/<int:pk>', views.OrganisationDocsStorageDetailView.as_view(), name='docs-detail'),
    path('docs/<int:pk>/generate-current', views.OrganisationDocsGenerateCurrentView.as_view(), name='generate'),
    path('docs/<int:pk>/download/<slug:type>', views.send_document, name='docs-download'),

    path('<int:pk>/checks', views.OrganisationChecksListView.as_view(), name='checks'),
    path('<int:pk>/current-checks', views.OrganisationCurrentChecksListView.as_view(), name='current-checks'),

    path('autocomplete', views.OrganisationAutocompleteView.as_view(), name='autocomplete'),
    path('autocomplete/node', views.OrganisationNodeAutocompleteView.as_view(), name='autocomplete-node'),
]