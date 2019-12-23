from django import forms
from .models import Message, MessageComment


class MessageForm(forms.ModelForm):

    body = forms.CharField(label='', widget=forms.Textarea(attrs={
        'name': 'enter-message', 'class': 'form-control mb-3', 'rows': '1', 'cols': '1',
        'placeholder': 'Введите сообщение...', 'id': 'message-body-input'}))

    class Meta:
        model = Message
        fields = ('body', 'chat', 'author')
        widgets = {
            'chat': forms.HiddenInput,
            'author': forms.HiddenInput
        }

    def __init__(self, *args, **kwargs):

        chat = kwargs.pop('chat', None)
        author = kwargs.pop('author', None)

        super().__init__(*args, **kwargs)

        self.fields['chat'].initial = chat
        self.fields['author'].initial = author


class CommentForm(forms.ModelForm):
    class Meta:
        model = MessageComment
        fields = ('body', 'author', 'message')
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control mb-3', 'rows': '1', 'cols': '1','placeholder': 'Введите комментарий...'}),
            'message': forms.HiddenInput,
            'author': forms.HiddenInput
        }

    def __init__(self, *args, **kwargs):
        author = kwargs.pop('author', None)
        super().__init__(*args, **kwargs)
        self.fields['author'].initial = author
