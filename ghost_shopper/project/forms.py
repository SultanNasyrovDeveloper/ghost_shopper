from dal import autocomplete as ac
from django import forms
from django.urls import reverse_lazy

from ghost_shopper.check.models import Check
from ghost_shopper.user_profile.models import User
from ghost_shopper.organisation_tree.models import OrganisationTreeNode
from ghost_shopper.check.enums import CHECK_TYPES

from .models import Project


class ProjectForm(forms.ModelForm):

    targets = forms.ModelMultipleChoiceField(
        queryset=OrganisationTreeNode.objects.exclude(level=0),
        widget=ac.ModelSelect2Multiple(url=reverse_lazy('organisation:autocomplete-node')))

    class Meta:
        model = Project
        fields = ('name', 'targets')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }


class ProjectCheckTemplateForm(forms.ModelForm):
    curator = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True), widget=forms.Select(
        attrs={'class': 'form-control form-control-uniform', 'placeholder': 'Куратор'}), label='Куратор')

    class Meta:
        model = Check
        fields = (
            'start_date', 'deadline', 'curator', 'reward', 'conformation_period', 'comment', 'instruction', 'kind')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control pickadate'}),
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control pickadate'}),
            'reward': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Награда (руб)'}),
            'conformation_period': forms.NumberInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Комментарий', 'rows': 3}),
            'instruction': ac.Select2(url=reverse_lazy('instruction:autocomplete')),
            'kind':  forms.Select(attrs={'class': 'form-control form-control-uniform', 'placeholder': 'Тип'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get('start_date'):
            initial = self.initial['start_date']
            self.fields['start_date'].widget.attrs['data-value'] = initial.strftime('%Y-%m-%d')
        if self.initial.get('deadline'):
            initial = self.initial['deadline']
            self.fields['deadline'].widget.attrs['data-value'] = initial.strftime('%Y-%m-%d')

