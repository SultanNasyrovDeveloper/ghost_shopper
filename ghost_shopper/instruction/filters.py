import django_filters as filters
from dal import autocomplete as ac
from django.urls import reverse_lazy

from .models import Instruction


class InstructionSearch(filters.FilterSet):

    id = filters.CharFilter(widget=ac.Select2(url=reverse_lazy('instruction:search-autocomplete'),
                                                attrs={'data-placeholder': 'Поиск'}))

    class Meta:
        model = Instruction
        fields = ('id', )
