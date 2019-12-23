from datetime import date

from dal import autocomplete as ac
from django import forms
from django.urls import reverse_lazy

from ghost_shopper.auth.forms import SignUpForm
from ghost_shopper.user_profile.models import PerformerProfile, CustomerProfile, PerformerAuto

from . import models


class StaffCreationForm(SignUpForm):

    is_staff = forms.BooleanField(initial=True, widget=forms.HiddenInput())

    class Meta:
        model = models.User
        fields = ('username', 'email', 'password1', 'password2', 'is_staff')


class StaffPermissionsForm(forms.ModelForm):

    class Meta:
        model = models.User
        fields = ('is_superuser', 'user_permissions', 'groups')


class PerformerCreationForm(SignUpForm):

    is_performer = forms.BooleanField(initial=True, widget=forms.HiddenInput())

    class Meta:
        model = models.User
        fields = ('username', 'email', 'password1', 'password2', 'is_performer')

    def save(self, *args, **kwargs):
        performer = super().save(*args, **kwargs)
        PerformerProfile.objects.create(user=performer)
        return performer


class CustomerCreationForm(SignUpForm):

    is_customer = forms.BooleanField(initial=True, widget=forms.HiddenInput())
    organisation_id = forms.IntegerField(required=True, widget=forms.HiddenInput())

    class Meta:
        model = models.User
        fields = ('username', 'email', 'password1', 'password2', 'is_customer', 'organisation_id')

    def __init__(self, *args, **kwargs):
        organisation_id = kwargs.pop('organisation_id')
        super().__init__(*args, **kwargs)
        self.fields['organisation_id'].initial = organisation_id

    def save(self, *args, **kwargs):
        customer = super().save(*args, **kwargs)
        if self.cleaned_data['organisation_id']:
            CustomerProfile.objects.create(
                user=customer, organisation_tree_node_id=self.cleaned_data['organisation_id'])
        return customer


class UserForm(forms.ModelForm):

    class Meta:
        model = models.User
        fields = ('last_name', 'email', 'first_name', 'patronymic', 'avatar', 'phone_number')
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Дмитрий'}),

            'patronymic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Алексеевич'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.ru'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'phone_number_input', 'placeholder': '+7 (789) 123-4567'}),
        }


class PerformerProfileForm(forms.ModelForm):

    class Meta:
        model = models.PerformerProfile
        fields = (
            'birth_date', 'city', 'work_cities', 'education', 'work_place', 'position', 'additional', 'staff_comment')
        widgets = {
            'city': forms.Select(attrs={'class': 'form-control'}),
            'work_cities': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'education': forms.Select(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control pickadate'}),
            'work_place': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Сбербанк'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Менеджер по продажам'}),
            'additional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Любая полезная информация'}),
            'staff_comment': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Информация для персонала'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get('birth_date', None):
            current_initial = self.initial['birth_date']
            self.fields['birth_date'].widget.attrs['data-value'] = current_initial.strftime('%Y-%m-%d')


class ApproveRequestDeclineForm(forms.ModelForm):
    notes = forms.CharField(label='Причины отклонения', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = models.PerformerApproveRequest
        fields = ('notes', 'performer_profile')
        widgets = {'performer_profile': forms.HiddenInput}


class PerformerAutoForm(forms.ModelForm):
    owner = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = models.PerformerAuto
        fields = ('owner', 'brand', 'model', 'built_year', 'owns_from')
        widgets = {
            'brand': ac.ModelSelect2(url=reverse_lazy('profile:car-brand-autocomplete'), attrs={
                'data-placeholder': 'Марка авто'
            }),
            'model': ac.ModelSelect2(url=reverse_lazy('profile:car-model-autocomplete'), forward=['brand'], attrs={
                'data-placeholder': 'Модкль автомобиля'
            }),
            'built_year': forms.NumberInput(attrs={'class': 'form-control', 'min': "1990", 'max': date.today().year}),
            'owns_from': forms.NumberInput(attrs={'class': 'form-control', 'min': "1990", 'max': date.today().year}),
        }

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        self.fields['owner'].initial = owner

    def save(self, *args, **kwargs):
        profile = PerformerProfile.objects.get(user_id=self.cleaned_data['owner'])
        self.cleaned_data.pop('owner')
        auto = PerformerAuto.objects.create(performer_profile=profile, **self.cleaned_data)
        return auto





