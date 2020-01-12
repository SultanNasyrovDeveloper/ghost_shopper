from django.urls import path

from . import views


app_name = 'core'


urlpatterns = [
    path('my-organisation', views.MyOrganisationUpdateView.as_view(), name='my-organisation'),

    path('check-kind', views.CheckKindListView.as_view(), name='check-kind-list'),
    path('check-kind/<int:pk>/update', views.CheckKindUpdateView.as_view(), name='check-kind-update'),
    path('check-kind/<int:pk>/delete', views.CheckKindDeleteView.as_view(), name='check-kind-delete'),

    path('section-name', views.SectionListView.as_view(), name='section_name_list'),
    path('section-name/<int:pk>/update', views.SectionUpdateView.as_view(), name='section-name-update'),
    path('section-name/<int:pk>/delete', views.SectionDeleteView.as_view(), name='section-name-delete'),

    path('city', views.CityListView.as_view(), name='city-list'),
    path('city/<int:pk>/delete', views.CityDeleteView.as_view(), name='city-delete'),

    path('car-brand', views.CarBrandListView.as_view(), name='car-brand-list'),
    path('car-brand/<int:pk>/delete', views.CarBrandDeleteView.as_view(), name='car-brand-delete'),

    path('car-brand/<int:pk>/models', views.CarModelListView.as_view(), name='car-model-list'),
    path('car-model/<int:pk>/delete', views.CarModelDeleteView.as_view(), name='car-model-delete'),

    path(
        'performer-letters-templates',
        views.PerformerLettersTemplateUpdateView.as_view(),
        name='performer-letters-template'
    )

]