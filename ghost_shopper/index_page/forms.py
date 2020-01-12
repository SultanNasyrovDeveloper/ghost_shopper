from django import forms


from . import models


class IndexPageForm(forms.ModelForm):
    logo = forms.FileField(required=False, label='Логотип')

    title = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Тег title',
    )
    keywords = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Тег keywords',
    )
    description = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Тег description',
    )
    phone_number = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Номер телефона',
    )
    email = forms.EmailField(
        required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Электронная почта',
    )
    header_background = forms.FileField(required=False, label='Фоновое изображение')
    header_tagline = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Заголовок',
    )
    header_subtagline = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Подзаголовок',
    )
    company_name = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Название компании',
    )
    about_text = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Текст о нас',
    )


    class Meta:
        model = models.IndexPage
        fields = (
            'logo', 'title', 'keywords', 'description', 'phone_number', 'header_background', 'header_tagline',
            'header_subtagline', 'phone_number', 'email', 'company_name', 'about_text',
        )


class CallbackForm(forms.ModelForm):

    class Meta:
        model = models.CallbackForm
        fields = ('name', 'phone_number')
