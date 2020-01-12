import django_filters as filters
from dal import autocomplete as ac
from django.urls import reverse_lazy
from django import forms
from dateutil.relativedelta import relativedelta
from datetime import date

from .models import User


class UserSearch(filters.FilterSet):

    id = filters.NumberFilter(
        label='',
        widget=ac.Select2(url=reverse_lazy('profile:autocomplete'), attrs={'data-placeholder': 'Поиск'})
    )

    class Meta:
        model = User
        fields = ('id', 'is_customer', 'is_staff')
        widgets = {
            'is_customer': forms.HiddenInput(),
            'is_staff': forms.HiddenInput(),
        }





