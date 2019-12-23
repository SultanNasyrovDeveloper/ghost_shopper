from django import forms
from .models import Instruction
from django_summernote.widgets import SummernoteWidget


class InstructionForm(forms.ModelForm):

    class Meta:
        model = Instruction
        fields = ('body', 'name')
        widgets = {
            'body': SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': 720}}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название инструкции'})
        }
