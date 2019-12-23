from django import forms
from django.contrib.auth.models import Group

from ghost_shopper.checklist.models import SectionName

from . import models


class MyOrganisationForm(forms.ModelForm):
    class Meta:
        model = models.MyOrganisation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'


class CheckKindForm(forms.ModelForm):
    class Meta:
        model = models.CheckKind
        fields = ('name', 'price')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'})
        }


class SectionNameForm(forms.ModelForm):
    class Meta:
        model = SectionName
        fields = ('value', )
        widgets = {'value': forms.TextInput(attrs={'class': 'form-control'})}


class CityForm(forms.ModelForm):
    class Meta:
        model = models.City
        fields = ('name', )
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}


class CarBrandForm(forms.ModelForm):
    class Meta:
        model = models.CarBrand
        fields = ('name', )
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}


class CarModelForm(forms.ModelForm):

    class Meta:
        model = models.CarModel
        fields = ('brand', 'name')
        widgets = {'brand': forms.HiddenInput(), 'name': forms.TextInput(attrs={'class': 'form-control'})}


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'permissions')


class PerformerInvitationLetterForm(forms.ModelForm):
    class Meta:
        model = models.PerformerLettersTemplates
        fields = ('invite_message', 'apply_message')
        widgets = {
            'invite_message': forms.TextInput(attrs={'class': 'form-control'}),
            'apply_message': forms.TextInput(attrs={'class': 'form-control'})
        }
