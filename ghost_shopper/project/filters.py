import django_filters as filters
from dal import autocomplete as ac
from django.urls import reverse_lazy

from .models import Project


class ProjectSearch(filters.FilterSet):
    name = filters.CharFilter(
        widget=ac.Select2(attrs={'data-placeholder': 'Поиск'}, url=reverse_lazy('project:autocomplete')))

    class Meta:
        model = Project
        fields = ('name', )
