from dal import autocomplete as ac
from dateutil.relativedelta import relativedelta
from datetime import date
from django import forms
from django.urls import reverse_lazy

from ghost_shopper.core.models import City
from . import models


class PerformerFilterSetForm(forms.Form):
    """
    Form for performer filter set.
    """
    id = forms.IntegerField(
        label='Поиск',
        required=False,
        widget=ac.ListSelect2(url=reverse_lazy('profile:performer-autocomplete'), attrs={'data-placeholder': 'Поиск'})
    )
    is_approved = forms.NullBooleanField(
        required=False,
        label='Профиль одобрен',
        widget=forms.NullBooleanSelect(attrs={'class': 'custom-select'})
    )
    age_gt = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'value': 18, 'min': '18', 'max': '99', 'type': 'range', 'step': 1,})
    )
    age_lt = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'value': 99, 'min': '18', 'max': '99', 'type': 'range', 'step': 1})
    )
    vehicle_age_gt = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'value': 0, 'min': '0', 'max': '30', 'type': 'range', 'step': 1})
    )
    vehicle_age_lt = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'value': 30,'min': '0','max': '30','type': 'range','step': 1 })
    )
    education = forms.MultipleChoiceField(
        required=False,
        choices=models.PerformerProfile.education_types,
        widget=forms.SelectMultiple(attrs={'class': 'multiselect'})
    )
    live_city = forms.ModelMultipleChoiceField(
        required=False,
        queryset=City.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'multiselect'})
    )
    work_city = forms.ModelMultipleChoiceField(
        required=False,
        queryset=City.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'multiselect'})
    )


class PerformerFilterSet:
    def __init__(self, queryset, get_parameters=None):
        self.form = PerformerFilterSetForm()
        self.queryset = queryset
        self.get_parameters = get_parameters

    @property
    def qs(self):
        if self.get_parameters:
            self.filter()
        return self.queryset

    def filter(self):
        self.filter_by_id()
        self.filter_by_is_approved()
        self.filter_by_age_gt()
        self.filter_by_age_lt()
        self.filter_by_vehicle_age_gt()
        self.filter_by_vehicle_age_lt()
        self.filter_by_education()
        self.filter_by_live_city()
        self.filter_by_work_city()

    def parameter_exists(self, parameter_name):
        """ """
        return parameter_name in self.get_parameters and self.get_parameters.get(parameter_name)

    def filter_by_id(self):
        """ Filters initial queryset by performer id """
        if self.parameter_exists('id'):
            self.queryset = self.queryset.filter(id=int(self.get_parameters.get('id')))

    def filter_by_is_approved(self):
        if self.parameter_exists('is_approved') and self.get_parameters.get('is_approved') != 'unknown':
            if self.get_parameters.get('is_approved') == 'true':
                self.queryset = self.queryset.filter(performer_profile__is_approved=True)
                self.form.fields['is_approved'].initial = True
            else:
                self.queryset = self.queryset.filter(performer_profile__is_approved=False)
                self.form.fields['is_approved'].initial = False

    def filter_by_age_gt(self):
        if self.parameter_exists('age_gt'):
            age = int(self.get_parameters.get('age_gt'))
            relative_date = date.today() + relativedelta(years=-age)
            self.queryset = self.queryset.filter(performer_profile__birth_date__lt=relative_date)
            self.form.fields['age_gt'].initial = age

    def filter_by_age_lt(self):
        if self.parameter_exists('age_lt'):
            age = int(self.get_parameters.get('age_lt'))
            relative_date = date.today() + relativedelta(years=-age)
            self.queryset = self.queryset.filter(performer_profile__birth_date__gt=relative_date)
            self.form.fields['age_lt'].initial = age

    def filter_by_vehicle_age_gt(self):
        if self.parameter_exists('vehicle_age_gt'):
            age = int(self.get_parameters.get('vehicle_age_gt'))
            relative_year = (date.today() + relativedelta(years=-age)).year
            self.queryset = self.queryset.filter(performer_profile__autos__built_year__lt=relative_year)
            self.form.fields['vehicle_age_gt'].initial = age

    def filter_by_vehicle_age_lt(self):
        if self.parameter_exists('vehicle_age_lt'):
            age = int(self.get_parameters.get('vehicle_age_lt'))
            relative_year = (date.today() + relativedelta(years=-age)).year
            self.queryset = self.queryset.filter(performer_profile__autos__built_year__gt=relative_year)
            self.form.fields['vehicle_age_lt'].initial = age

    def filter_by_education(self):
        if self.parameter_exists('education'):
            education = self.get_parameters.getlist('education')
            self.queryset = self.queryset.filter(performer_profile__education__in=education)
            self.form.fields['education'].initial = education

    def filter_by_live_city(self):
        if self.parameter_exists('live_city'):
            live_cities = self.get_parameters.getlist('live_city')
            self.queryset = self.queryset.filter(performer_profile__city__in=live_cities)
            self.form.fields['live_city'].initial = live_cities

    def filter_by_work_city(self):
        if self.parameter_exists('work_city'):
            work_cities = self.get_parameters.getlist('work_city')
            self.queryset = self.queryset.filter(performer_profile__city__in=work_cities)
            self.form.fields['live_city'].initial = work_cities

