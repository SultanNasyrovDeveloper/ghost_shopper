from django import forms
from django_summernote.widgets import SummernoteWidget

from ghost_shopper.checklist.models import (Checklist, GeneralAnswer,
                                            IntegerQuestionOption, Question,
                                            Section, SectionName,
                                            TextQuestionOption)


class SectionForm(forms.ModelForm):
    """ """

    upper_section_id = forms.IntegerField(required=False, widget=forms.HiddenInput(attrs={':value': 'upperSectionId'}))
    name = forms.ModelChoiceField(
        queryset=SectionName.objects.all(), required=True, widget=forms.Select(attrs={'class': 'custom-select'}))
    parent_id = forms.IntegerField(required=False, widget=forms.HiddenInput(attrs={':value': 'parentSectionId'}))

    class Meta:
        model = Section
        fields = ('checklist', 'name', 'parent_id')
        widgets = {
            'checklist': forms.HiddenInput(attrs={':value': 'checklist.id'})}

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if self.cleaned_data.get('parent_id', None):
            parent = Section.objects.get(id=int(self.cleaned_data['parent_id']))
            instance.parent = parent
        if self.cleaned_data.get('upper_section_id'):
            upper_section = Section.objects.get(id=self.cleaned_data.get('upper_section_id'))
            instance.below(upper_section)
        instance.save()
        return instance


class QuestionForm(forms.ModelForm):
    """ """
    upper_question_id = forms.IntegerField(required=False, widget=forms.HiddenInput(attrs={':value': 'upperQuestionId'}))
    section_id = forms.IntegerField(required=True, widget=forms.HiddenInput(attrs={':value': 'newQuestionSectionId'}))

    class Meta:
        model = Question
        fields = ('section_id', 'text', 'type')
        widgets = {
            'type': forms.HiddenInput(attrs={':value': 'newQuestionType'}),
            'text': forms.Textarea(attrs={'class': 'summernote'}),
        }

    def save(self, commit=True):
        """"""
        section = Section.objects.get(id=self.cleaned_data['section_id'])
        question = Question.objects.create(section=section, text=self.cleaned_data['text'],
                                           type=self.cleaned_data['type'])
        return question


class GeneralAnswerForm(forms.ModelForm):
    """ """
    class Meta:
        model = GeneralAnswer
        fields = ('positive_answer_value', )
        widgets = {
            'positive_answer_value': forms.NumberInput(attrs={'class': 'form-control'})
        }

    def save(self, commit=True):
        answer = GeneralAnswer.objects.create(
            question_id=self.cleaned_data['question_id'],
            positive_answer_value=self.cleaned_data['positive_answer_value'])
        return answer


class IntQuestionOptionForm(forms.ModelForm):
    """ """
    upper_option_id = forms.IntegerField(required=False, widget=forms.HiddenInput(attrs={':value': 'upperOptionId'}))

    class Meta:
        model = IntegerQuestionOption
        fields = ('question', 'value', 'points', 'upper_option_id')
        widgets = {
            'question': forms.HiddenInput(attrs={':value': 'newOptionQuestionId'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
            'points': forms.NumberInput(attrs={'class': 'form-control'})
        }

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if self.cleaned_data.get('upper_option_id', None):
            upper_option = IntegerQuestionOption.objects.get(id=int(self.cleaned_data['upper_option_id']))
            instance.below(upper_option)
        return instance


class TextQuestionOptionForm(forms.ModelForm):
    """ """
    upper_option_id = forms.IntegerField(required=False, widget=forms.HiddenInput(attrs={':value': 'upperOptionId'}))

    class Meta:
        model = TextQuestionOption
        fields = ('question', 'value', 'upper_option_id')
        widgets = {
            'question': forms.HiddenInput(attrs={':value': 'newOptionQuestionId'}),
            'value': forms.TextInput(attrs={'class': 'form-control'})
        }

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if self.cleaned_data.get('upper_option_id', None):
            upper_option = TextQuestionOption.objects.get(id=int(self.cleaned_data['upper_option_id']))
            instance.below(upper_option)
        return instance
