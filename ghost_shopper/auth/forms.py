from django import forms
from django.contrib.auth import forms as auth_forms

from ghost_shopper.user_profile.models import PerformerProfile, User


class LoginForm(auth_forms.AuthenticationForm):
    """Custom login form."""
    username = auth_forms.UsernameField(widget=forms.TextInput(attrs={
        'autofocus': True, 'class': 'form-control', 'placeholder': 'Введите логин'})
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Введите пароль', 'class': 'form-control'}
        ),
    )


class SignUpForm(auth_forms.UserCreationForm):
    """Custom registration form."""

    username = auth_forms.UsernameField(widget=forms.TextInput(
        attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'Введите логин'})
    )
    email = forms.EmailField(
        required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'})
    )
    password1 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}),
        help_text=auth_forms.password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Подтвердите пароль"}),
        strip=False,
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class PerformerSignUpForm(SignUpForm):
    """Custom creation form for performer users."""

    is_performer = forms.BooleanField(initial=True, widget=forms.HiddenInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'is_performer')

    def save(self, *args, **kwargs):
        """Create performer user and performer profile instance."""
        user = super().save()
        PerformerProfile.objects.create(user=user)
        return user


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    """Password change form."""
    old_password = forms.CharField(
        label='Старый пароль',
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'Старый пароль'}
        ),
    )
    new_password1 = forms.CharField(
        label='',
        widget=forms.PasswordInput(
            attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'Новый пароль'}
        ),
        strip=False,
        help_text=auth_forms.password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'Подтвердите пароль'}
        ),
    )


class PasswordResetForm(auth_forms.PasswordResetForm):
    """Password reset form."""
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'})
    )


class SetPasswordForm(auth_forms.SetPasswordForm):
    """Set new password form."""
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput({'autofocus': True, 'class': 'form-control', 'placeholder': 'Новый пароль'}),
        strip=False,
        help_text=auth_forms.password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label="Подтвердите новый пароль",
        strip=False,
        widget=forms.PasswordInput({
            'autofocus': True, 'class': 'form-control', 'placeholder': 'Подтвердите новый пароль'}),
    )
