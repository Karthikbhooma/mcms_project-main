"""
Complaints Forms
Complaint submission and management forms
"""

from django import forms
from .models import Complaint
from departments.models import Department
import os


class ComplaintForm(forms.ModelForm):
    """
    Complaint submission form with file upload validation
    """
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-input',
            'id': 'id_department'
        }),
        empty_label="-- Select Department --"
    )
    
    
    ward_number = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter ward number (e.g., Ward 12)'
        })
    )
    
    area = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter area/locality name'
        })
    )
    
    landmark = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nearby landmark (optional)'
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Brief subject of complaint'
        })
    )
    
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Detailed description of the complaint...',
            'rows': 6
        })
    )
    
    proof_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-input',
            'accept': '.jpg,.jpeg,.png,.pdf',
            'id': 'id_proof_file'
        })
    )
    
    class Meta:
        model = Complaint
        fields = [
            'department', 'ward_number', 'area', 
            'landmark', 'subject', 'description', 'proof_file'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def clean_proof_file(self):
        """
        Validate uploaded file type and size
        """
        file = self.cleaned_data.get('proof_file')
        
        if file:
            # Check file size (5MB max)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size cannot exceed 5MB.')
            
            # Check file extension
            ext = os.path.splitext(file.name)[1].lower()
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
            
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}'
                )
        
        return file
    
    def clean_ward_number(self):
        """Validate ward number format"""
        ward = self.cleaned_data.get('ward_number')
        
        if ward:
            ward = ward.strip()
            if len(ward) < 1:
                raise forms.ValidationError('Ward number is required.')
        
        return ward
    
    def clean_description(self):
        """Validate description length"""
        description = self.cleaned_data.get('description')
        
        if description and len(description) < 20:
            raise forms.ValidationError('Please provide a detailed description (minimum 20 characters).')
        
        return description


class ComplaintFilterForm(forms.Form):
    """
    Filter form for admin panel
    """
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Complaint.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'}),
        empty_label="All Departments"
    )
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Search by Complaint ID or Subject'
        })
    )
