from django import forms


from . import models


class IndexPageForm(forms.ModelForm):
    title = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    keywords = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = models.IndexPage
        fields = ('__all__')
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'header_tagline': forms.TextInput(attrs={'class': 'form-control'}),
            'header_subtagline': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'about_text': forms.TextInput(attrs={'class': 'form-control'}),

        }


class CallbackForm(forms.ModelForm):

    class Meta:
        model = models.CallbackForm
        fields = ('name', 'phone_number')
