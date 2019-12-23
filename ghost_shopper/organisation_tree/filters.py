import django_filters as filters

from django.urls import reverse_lazy
from dal import autocomplete

from .models import OrganisationTreeNode, OrganisationMonthlyDocumentStorage


class OrganisationSearch(filters.FilterSet):
    name = filters.CharFilter(label='', widget=autocomplete.ListSelect2(
        url=reverse_lazy('organisation:autocomplete'), attrs={'data-placeholder': 'Поиск'}))

    class Meta:
        model = OrganisationTreeNode
        fields = ('name', )


class OrganisationDocumentFilter(filters.FilterSet):
    class Meta:
        model = OrganisationMonthlyDocumentStorage
        fields = ('organisation', 'date')
