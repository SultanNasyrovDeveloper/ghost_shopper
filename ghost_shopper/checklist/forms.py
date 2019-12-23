from django import forms
from multiupload.fields import MultiFileField

from .models import (Checklist, GeneralAnswer, Image, IntegerChoicesAnswer,
                     IntegerQuestionOption, OpenAnswer, TextChoicesAnswer,
                     TextQuestionOption)


class ChecklistMediaForm(forms.ModelForm):
    images = MultiFileField(required=False)
    audio = forms.FileField(required=False, widget=forms.FileInput(attrs={
        'id': 'audio-input', 'accept': 'audio/*', 'class': 'form-control'}))
    visit_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date', 'class': 'form-control pickadate', 'placeholder': 'Введите дату визита'})
    )

    class Meta:
        model = Checklist
        fields = ('audio', 'images', 'visit_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get('visit_date', None):
            initial = self.initial['visit_date']
            self.fields['visit_date'].widget.attrs['data-value'] = initial.strftime('%Y-%m-%d')

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        for image in self.cleaned_data['images']:
            Image.objects.create(checklist=instance, file=image)
        return instance

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('visit_date', None):
            raise forms.ValidationError('Дата визита обязательное поле')
        return cleaned_data


class AnswerFormBase(forms.ModelForm):
    performer_comment = forms.CharField(required=False, label='', widget=forms.Textarea(attrs={
        'placeholder': 'Комментарий к ответу',
        'class': 'form-control',
        'rows': 1
    }))
    appeal_comment = forms.CharField(required=False, label='', widget=forms.Textarea(attrs={
        'placeholder': 'Текст аппеляции',
        'class': 'form-control',
        'rows': 1
    }))
    appeal_answer = forms.CharField(required=False, label='', widget=forms.Textarea(attrs={
        'placeholder': 'Ответ на аппеляцию',
        'class': 'form-control',
        'rows': 1
    }))


class GeneralAnswerForm(AnswerFormBase):
    """  """
    answer = forms.NullBooleanField(widget=forms.RadioSelect(choices=[(True, 'Да'), (False, 'Нет')]), required=False)

    class Meta:
        model = GeneralAnswer
        fields = ('answer', 'performer_comment', 'appeal_comment', 'appeal_answer')

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data['answer'] is False and not cleaned_data['performer_comment']:
            raise forms.ValidationError('Вы должны указать комментарий для отрицательного ответа')
        else:
            return self.cleaned_data


class OpenAnswerForm(AnswerFormBase):
    """ """
    class Meta:
        model = OpenAnswer
        fields = ('answer', 'performer_comment', 'appeal_comment', 'appeal_answer')
        widgets = {'answer': forms.TextInput(attrs={'class': 'form-control'})}


class IntegerChoicesAnswerForm(AnswerFormBase):
    """"""
    class Meta:
        model = IntegerChoicesAnswer
        fields = ('answer', 'performer_comment', 'appeal_comment', 'appeal_answer')
        widgets = {'answer': forms.Select(attrs={'class': 'form-control'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = IntegerQuestionOption.objects.filter(question_id=self.instance.question_id)


class TextChoicesAnswerForm(AnswerFormBase):
    """ """
    class Meta:
        model = TextChoicesAnswer
        fields = ('answer', 'performer_comment', 'appeal_comment', 'appeal_answer')
        widgets = {'answer': forms.Select(attrs={'class': 'form-control'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = TextQuestionOption.objects.filter(question_id=self.instance.question_id)
