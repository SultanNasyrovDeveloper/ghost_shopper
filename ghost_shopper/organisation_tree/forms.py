from django import forms
from django.db.models import Q

from ghost_shopper.core.models import City

from . import models


class OrganisationForm(forms.ModelForm):

    name = forms.CharField(
        label='Название организации',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'СуперСервисПро'}),
    )

    class Meta:
        model = models.OrganisationTreeNode
        fields = (
            'name', 'full_name', 'docs_generating_type', 'checks_theme', 'contract_name', 'INN', 'KPP', 'legal_address'
        )
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ООО "СуперСервисПро"'}),
            'checks_theme': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Аудит качества обслуживания в автосалоне Заказчика'
            }),
            'contract_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Договор № 3 от 01.01.2010'
            }),
            'INN': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567891012'}),
            'KPP': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123456789'}),
            'legal_address': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Москва ул. Лесная, 23'
                }),
            'docs_generating_type': forms.Select(attrs={'class': 'form-control'}),
        }


class LocationForm(OrganisationForm):
    """
    Organisation form for 2nd level nodes.
    """
    name = forms.CharField(
        label='Название организации',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'СуперСервисПро'}),
    )

    parent = forms.ModelChoiceField(
        widget=forms.HiddenInput, queryset=models.OrganisationTreeNode.objects.filter(level__in=(0, 1)),
    )
    city = forms.ModelChoiceField(
        label='Город',
        required=True,
        queryset=City.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ул. Московская, 12'}),
        label='Адрес')

    class Meta(OrganisationForm.Meta):
        model = models.OrganisationTreeNode
        fields = (
            'name', 'full_name', 'city', 'address', 'checks_theme', 'contract_name', 'INN', 'KPP', 'legal_address',
            'parent',
        )

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


