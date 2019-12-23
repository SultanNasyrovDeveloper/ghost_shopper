from django import forms
from django.db.models import Q

from ghost_shopper.core.models import City

from . import models


class OrganisationForm(forms.ModelForm):

    name = forms.CharField(
        label='Название',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название организации'}),
    )

    class Meta:
        model = models.OrganisationTreeNode
        fields = [
            'name', 'full_name', 'docs_generating_type', 'checks_theme', 'contract_name', 'INN', 'KPP', 'legal_address'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Полное имя'}),
            'checks_theme': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Тема проверок'}),
            'contract_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название договора'}),
            'INN': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ИНН'}),
            'KPP': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'КПП'}),
            'legal_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Юридический адрес'}),
            'docs_generating_type': forms.Select(attrs={'class': 'form-control'}),
        }


class LocationForm(OrganisationForm):
    """
    Organisation form for 2nd level nodes.

    """

    parent = forms.ModelChoiceField(
        label='Название',
        widget=forms.HiddenInput, queryset=models.OrganisationTreeNode.objects.filter(level__in=(0, 1)),
    )
    city = forms.ModelChoiceField(
        label='Город',
        required=True,
        queryset=City.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta(OrganisationForm.Meta):
        model = models.OrganisationTreeNode
        fields = [
            'name', 'full_name', 'city', 'address', 'checks_theme', 'contract_name', 'INN', 'KPP', 'legal_address',
            'parent',
        ]

    def __init__(self, *args, **kwargs):
        """
        Initialize class.
        """
        parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        if parent:
            self.fields['parent'].initial = parent


class DepartmentUpdateForm(forms.ModelForm):
    """
    Department node update form.
    """

    name = forms.CharField(
        label='Название',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название организации'}),
    )

    class Meta:
        model = models.OrganisationTreeNode
        fields = ('name', )


class DepartmentForm(forms.ModelForm):

    parent = forms.ModelChoiceField(widget=forms.HiddenInput, queryset=models.OrganisationTreeNode.objects.filter(
        level__in=(0, 1)
    ))

    class Meta:
        model = models.OrganisationTreeNode
        fields = ('name', 'parent')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название отдела'})
        }

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent')
        super().__init__(*args, **kwargs)
        self.fields['parent'].initial = parent


