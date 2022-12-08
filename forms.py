from django import forms

class postForm(forms.Form):
    textarea = forms.CharField(label="New post",label_suffix="", widget=forms.Textarea(attrs={
        'placeholder': 'Your post here'
    }))