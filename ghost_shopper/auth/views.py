from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from . import forms


class SignUpView(generic.CreateView):
    """New user sign up view."""

    template_name = 'auth/signup.html'
    form_class = forms.PerformerSignUpForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(reverse_lazy('profile:detail', args=(user.id, )))


class UserLogoutView(LoginRequiredMixin,  auth_views.LogoutView):
    """User logout view."""

    next_page = reverse_lazy('index_page:index')


class UserLoginView(auth_views.LoginView):
    """User login view."""

    template_name = 'auth/login.html'
    form_class = forms.LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        """Get url for redirecting logged in user."""
        url = reverse_lazy('profile:detail', args=(self.request.user.id,))
        if self.request.GET.get('next', None):
            url = self.request.GET['next']
        return url


class PasswordChangeView(LoginRequiredMixin, auth_views.PasswordChangeView):
    """Password change view."""

    form_class = forms.PasswordChangeForm
    template_name = 'auth/password_change.html'

    def get_success_url(self):
        return self.request.user.get_absolute_url()


class PasswordResetView(auth_views.PasswordResetView):
    """Password reset view."""

    template_name = 'auth/password_reset.html'
    email_template_name = 'auth/password_reset_email.html'
    subject_template_name = 'auth/password_reset_subject.txt'
    form_class = forms.PasswordResetForm
    success_url = reverse_lazy('auth:login')


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """Password reset confirm view"""
    template_name = 'auth/set_password.html'
    form_class = forms.SetPasswordForm
    success_url = reverse_lazy('auth:login')
    post_reset_login = True
