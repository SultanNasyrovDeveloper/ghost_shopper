from django.urls import path

from . import views

app_name = 'check'


urlpatterns = [

    # different check list urls
    path('', views.ChecksListView.as_view(), name='list'),
    path('available', views.AvailableChecksListView.as_view(), name='available'),
    path('performer/<int:pk>/closed', views.PerformerClosedChecksListView.as_view(), name='performer-closed'),
    path('performer/<int:pk>/current', views.PerformerCurrentChecksListView.as_view(), name='performer-current'),

    path('create', views.CheckCreateView.as_view(), name='create'),
    path('<int:pk>', views.CheckDetailView.as_view(), name='detail'),
    path('<int:pk>/update', views.CheckUpdateView.as_view(), name='update'),
    path('<int:pk>/delete', views.CheckDeleteView.as_view(), name='delete'),
    path('<int:pk>/excel', views.CheckFileGenerateView.as_view(), name='excel'),

    # check performer requests urls
    path('<int:pk>/appoint-performer', views.CheckAppointPerformerView.as_view(), name='appoint-performer'),
    path('<int:pk>/perform-request/create',
         views.CheckPerformRequestCreateView.as_view(),
         name='create-perform-request'),
    path('perform-request/<int:pk>/approve',
         views.CheckPerformRequestApproveView.as_view(),
         name='approve-perform-request'),

    # check change statuses urls
    path('<int:pk>/change-status/available', views.CheckMakeAvailableView.as_view(), name='make-available'),
    path('<int:pk>/make-processing', views.CheckMakeProcessingView.as_view(), name='make-processing'),
    path('<int:pk>/change-status/filled', views.CheckMakeFilledView.as_view(), name='make-filled'),
    path('<int:pk>/change-status/rework', views.CheckSendForReworkView.as_view(), name='make-rework'),
    path('<int:pk>/change-status/conformation',
        views.CheckSendForCustomerConformationView.as_view(),
        name='make-conformation'),
    path('<int:pk>/change-status/close', views.CheckCloseView.as_view(), name='make-close'),
]
