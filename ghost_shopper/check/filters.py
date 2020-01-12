import django_filters as filters
from dal import autocomplete as ac
from django import forms
from django.urls import reverse_lazy
from django_filters.widgets import RangeWidget

from ghost_shopper.user_profile.models import User
from ghost_shopper.core.models import CheckKind

from .enums import CheckStatusesEnum
from .models import Check


class CheckFilterSet(filters.FilterSet):
    """ """
    status = filters.MultipleChoiceFilter(choices=tuple(CheckStatusesEnum.values.items()))
    start_date = filters.DateFromToRangeFilter(widget=RangeWidget(attrs={'class': 'form-control pickadate mr-1 ml-1'}))
    end_date = filters.DateFromToRangeFilter(widget=RangeWidget(attrs={'class': 'form-control pickadate mr-1 ml-1'}))
    curator = filters.ModelChoiceFilter(
        queryset=User.objects.filter(is_staff=True), widget=forms.Select(attrs={'class': 'form-control'}))
    target = filters.CharFilter(widget=ac.ListSelect2(
        url=reverse_lazy('organisation:autocomplete-node'),
        attrs={'class': 'form-control', 'data-placeholder': 'Организация'}
    ))

    class Meta:
        model = Check
        fields = ('status', 'start_date', 'end_date', 'curator', 'target')


class OrganisationClosedChecksFilterSet(CheckFilterSet):
    class Meta:
        model = Check
        fields = ('start_date', 'end_date', 'curator', 'target')


class OrganisationChecksFilterset(filters.FilterSet):
    start_date__gt = filters.DateFilter(field_name='start_date', lookup_expr='gt')

    class Meta:
        model = Check
        fields = ('start_date__gt', )



class ChecksForStatisticsFilterSet(filters.FilterSet):
    """
    FilterSet that will be user to filter checks for organisation statistics check.

    """

    nodes = filters.ModelMultipleChoiceFilter(
        label='Цель проверки',
        field_name='target',
        widget=forms.SelectMultiple(attrs={'class': 'multiselect form-control'}),
    )
    visit_date__lte = filters.DateFilter(
        label='Дата проведения до',
        field_name='checklist__visit_date',
        lookup_expr='lte',
        widget=forms.DateInput(attrs={'class': 'pickadate form-control', 'type': 'date'}),
    )
    visit_date__gte = filters.DateFilter(
        label='Дата проведения от',
        field_name='checklist__visit_date',
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'class': 'pickadate form-control', 'type': 'date'}),
    )
    kind = filters.ModelMultipleChoiceFilter(
        label='Тип проверки',
        field_name='kind',
        widget=forms.SelectMultiple(attrs={'class': 'multiselect form-control'}),
        queryset=CheckKind.objects.all(),
    )

    class Meta:
        model = Check
        fields = ('nodes', 'visit_date__lte', 'visit_date__gte', 'kind')

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize class.

        Add queryset attribute to nodes class.
        """
        nodes = kwargs.pop('nodes')
        super().__init__(*args, **kwargs)
        self.filters['nodes'].queryset = nodes



