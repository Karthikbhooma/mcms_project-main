"""
Accounts Models - Citizen User Model
Custom user model for government-grade citizen authentication
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import random
import string


class CitizenManager(BaseUserManager):
    """
    Custom manager for Citizen model
    """
    
    def create_user(self, username, email, mobile, password=None, **extra_fields):
        """Create and save a regular citizen user"""
        if not username:
            raise ValueError('Username is required')
        if not email:
            raise ValueError('Email is required')
        if not mobile:
            raise ValueError('Mobile number is required')
        
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            mobile=mobile,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, mobile, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        
        return self.create_user(username, email, mobile, password, **extra_fields)


class Citizen(AbstractBaseUser, PermissionsMixin):
    """
    Custom Citizen User Model
    Extends Django's AbstractBaseUser for government-grade authentication
    """
    
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    mobile = models.CharField(max_length=15, unique=True)
    
    # User status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # OTP fields for email verification
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    
    objects = CitizenManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'mobile']
    
    class Meta:
        db_table = 'citizens'
        verbose_name = 'Citizen'
        verbose_name_plural = 'Citizens'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} - {self.mobile}"
    
    def generate_otp(self):
        """Generate 6-digit OTP for email verification"""
        self.otp = ''.join(random.choices(string.digits, k=6))
        self.otp_created_at = timezone.now()
        self.save()
        return self.otp
    
    def verify_otp(self, input_otp):
        """Verify OTP - valid for 10 minutes"""
        if not self.otp or not self.otp_created_at:
            return False
        
        # Check if OTP is expired (10 minutes)
        time_diff = timezone.now() - self.otp_created_at
        if time_diff.total_seconds() > 600:  # 10 minutes
            return False
        
        if self.otp == input_otp:
            self.is_verified = True
            self.otp = None
            self.otp_created_at = None
            self.save()
            return True
        
        return False
    
    def get_full_name(self):
        return self.username
    
    def get_short_name(self):
        return self.username


class LoginAttempt(models.Model):
    """
    Track login attempts for security monitoring
    """
    
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    attempted_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'login_attempts'
        verbose_name = 'Login Attempt'
        verbose_name_plural = 'Login Attempts'
        ordering = ['-attempted_at']
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.username} - {status} - {self.attempted_at}"
