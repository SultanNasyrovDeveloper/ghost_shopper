from django.urls import path

from . import views


app_name = 'auth'


urlpatterns = [
    path('signup/performer', views.SignUpView.as_view(), name='signup_performer'),
    path('logout', views.UserLogoutView.as_view(), name='logout'),
    path('login', views.UserLoginView.as_view(), name='login'),
    path('change-password', views.PasswordChangeView.as_view(), name='change_password'),
    path('reset-password', views.PasswordResetView.as_view(), name='reset-password'),
    path('reset-password/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm')
]
