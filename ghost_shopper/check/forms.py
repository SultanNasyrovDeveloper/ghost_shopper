from dal import autocomplete as ac
from django import forms
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from ghost_shopper.check.models import CheckPerformInvitation
from ghost_shopper.user_profile.models import User

from .enums import CheckStatusesEnum
from .models import Check, CheckPerformRequest


class CheckForm(forms.ModelForm):

    status = forms.ChoiceField(
        choices=tuple(CheckStatusesEnum.values.items()),
        label='Статус',
        widget=forms.Select(attrs={'class': 'form-control'}))
    curator = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True), widget=forms.Select(
        attrs={'class': 'form-control form-control-uniform', 'placeholder': 'Куратор'}), label='Куратор')

    class Meta:
        model = Check
        fields = (
            'status', 'start_date', 'deadline', 'target', 'performer', 'curator', 'reward',
            'conformation_period', 'comment', 'instruction', 'kind'
        )
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control pickadate'}),
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control pickadate'}),
            'target': ac.Select2(
                url=reverse_lazy('organisation:autocomplete-node'),
                attrs={'data-placeholder': 'Цель проверки'}
            ),
            'kind': forms.Select(attrs={'class': 'form-control form-control-uniform', 'placeholder': 'Тип'}),
            'performer': ac.Select2(
                url=reverse_lazy('profile:performer-autocomplete'),
                attrs={'data-placeholder': 'Тайный покупатель', 'class': 'form-control'}
            ),
            'reward': forms.NumberInput(attrs={
                'type': "number",
                'id': "qty_input",
                'class': "form-control form-control-sm",
                'value': "1",
                'min': "1",
                'placeholder': 'Награда (руб)'
            }),
            'conformation_period': forms.NumberInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Комментарий', 'rows': 3}),
            'instruction': ac.Select2(
                url=reverse_lazy('instruction:autocomplete'),
                attrs={'data-placeholder': 'Название инструкции'}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get('start_date', None):
            initial = self.initial['start_date']
            self.fields['start_date'].widget.attrs['data-value'] = initial.strftime('%Y-%m-%d')
        if self.initial.get('deadline', None):
            initial = self.initial['deadline']
            self.fields['deadline'].widget.attrs['data-value'] = initial.strftime('%Y-%m-%d')


class CheckPerformerAppointForm(forms.ModelForm):
    class Meta:
        model = Check
        fields = ('performer', )
        widgets = {
            'performer': ac.Select2(
                url=reverse_lazy('profile:performer-autocomplete'),
                attrs={'data-placeholder': 'Тайный покупатель'}),
        }

    def save(self, *args, **kwargs):
        check = super().save(*args, **kwargs)
        check.make_processing()
        return check


class PerformRequestForm(forms.ModelForm):
    class Meta:
        model = CheckPerformRequest
        fields = ('check_obj', 'performer')
        widgets = {
            'check_obj': forms.HiddenInput(),
            'performer': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        check = None
        if kwargs.get('check_id', None):
            check = get_object_or_404(Check.usual.all(), id=kwargs.pop('check_id'))
            performer = get_object_or_404(User.objects.filter(is_performer=True), id=kwargs.pop('performer_id'))

        super().__init__(*args, **kwargs)

        if check:
            self.fields['check_obj'].initial = check
            self.fields['performer'].initial = performer


class InvitePerformersForm(forms.Form):
    performers = forms.ModelMultipleChoiceField(queryset=None)
    check = forms.ModelChoiceField(
        queryset=Check.objects.filter(status=CheckStatusesEnum.AVAILABLE), widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('performers_qs')
        check = kwargs.pop('check', None)
        super().__init__(*args, **kwargs)
        self.fields['performers'].queryset = qs

        if check is not None:
            self.fields['check'].initial = check

    def save(self, *args, **kwargs):
        """ Create performer invitation for each of performers in the form """
        for performer in self.cleaned_data['performers']:
            CheckPerformInvitation.invite(performer=performer, check=self.cleaned_data['check'])
