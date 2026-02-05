"""
Accounts Forms - Registration, Login, OTP Verification
Government-grade form validation and security
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Citizen
import re


class CitizenRegistrationForm(UserCreationForm):
    """
    Citizen registration form with comprehensive validation
    """
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter username',
            'autocomplete': 'off'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter email address',
            'autocomplete': 'off'
        })
    )
    
    mobile = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter 10-digit mobile number',
            'autocomplete': 'off'
        })
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter password (min 8 characters)',
            'autocomplete': 'new-password'
        })
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Re-enter password',
            'autocomplete': 'new-password'
        })
    )
    
    captcha_input = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter CAPTCHA',
            'autocomplete': 'off'
        })
    )
    
    class Meta:
        model = Citizen
        fields = ['username', 'email', 'mobile', 'password1', 'password2']
    
    def clean_username(self):
        """Validate username - alphanumeric only"""
        username = self.cleaned_data.get('username')
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError('Username can only contain letters, numbers, and underscores.')
        
        if Citizen.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists. Please choose another.')
        
        return username
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        
        if Citizen.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered. Please use another email.')
        
        return email
    
    def clean_mobile(self):
        """Validate mobile number - Indian format"""
        mobile = self.cleaned_data.get('mobile')
        
        if not re.match(r'^[6-9]\d{9}$', mobile):
            raise forms.ValidationError('Enter a valid 10-digit Indian mobile number starting with 6-9.')
        
        if Citizen.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError('Mobile number already registered.')
        
        return mobile
    
    def clean_password2(self):
        """Validate password match"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        
        return password2


class CitizenLoginForm(AuthenticationForm):
    """
    Custom login form for citizens
    """
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter username',
            'autocomplete': 'username'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter password',
            'autocomplete': 'current-password'
        })
    )
    
    captcha_input = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter CAPTCHA',
            'autocomplete': 'off'
        })
    )


class OTPVerificationForm(forms.Form):
    """
    OTP verification form
    """
    
    otp = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter 6-digit OTP',
            'autocomplete': 'off',
            'maxlength': '6'
        })
    )
    
    def clean_otp(self):
        """Validate OTP format"""
        otp = self.cleaned_data.get('otp')
        
        if not re.match(r'^\d{6}$', otp):
            raise forms.ValidationError('OTP must be 6 digits.')
        
        return otp
