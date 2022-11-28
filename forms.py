from django import forms

class postForm(forms.Form):
    textarea = forms.CharField(label="New post", widget=forms.Textarea(attrs={
        'placeholder': 'Your post here'
    }))