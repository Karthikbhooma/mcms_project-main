"""
Admin Panel Forms
Admin authentication and complaint management
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from complaints.models import Complaint
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminLoginForm(AuthenticationForm):
    """
    Admin login form
    """
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter admin username'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter password'
        })
    )


class UpdateComplaintStatusForm(forms.ModelForm):
    """
    Form to update complaint status and add remarks
    """
    
    status = forms.ChoiceField(
        choices=Complaint.STATUS_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    
    official_remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Add official remarks (visible to citizen)...',
            'rows': 4
        })
    )

    officer = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    resolution_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Resolution details (internal)...',
            'rows': 3
        })
    )

    resolution_proof = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-input'})
    )
    
    class Meta:
        model = Complaint
        fields = ['status', 'official_remarks', 'officer', 'resolution_notes', 'resolution_proof']
