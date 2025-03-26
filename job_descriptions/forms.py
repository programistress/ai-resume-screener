from django import forms
from .models import JobDescription

class JobDescUploadForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = ['raw text']
        widgets = {
            'raw_test': forms.Textarea(attrs={'placeholder': 'Paste the job description here...'}),
        }