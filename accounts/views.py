"""
Accounts Views - Citizen Registration, Login, OTP Verification
Production-grade authentication system
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import Citizen, LoginAttempt
from .forms import CitizenRegistrationForm, CitizenLoginForm, OTPVerificationForm
from .captcha_utils import CaptchaGenerator


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip


def citizen_register(request):
    """
    Citizen registration with CAPTCHA and OTP verification
    """
    
    # Generate CAPTCHA for GET request
    if request.method == 'GET':
        if not request.session.session_key:
            request.session.create()
        
        captcha_text, captcha_filename = CaptchaGenerator.generate_and_save(
            request.session.session_key
        )
        request.session['captcha_text'] = captcha_text
        request.session['captcha_filename'] = captcha_filename
    
    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)
        
        # Verify CAPTCHA
        captcha_input = request.POST.get('captcha_input', '')
        captcha_stored = request.session.get('captcha_text', '')
        
        if captcha_input.upper() != captcha_stored.upper():
            messages.error(request, 'Invalid CAPTCHA. Please try again.')
            
            # Regenerate CAPTCHA
            captcha_text, captcha_filename = CaptchaGenerator.generate_and_save(
                request.session.session_key
            )
            request.session['captcha_text'] = captcha_text
            request.session['captcha_filename'] = captcha_filename
            
            return render(request, 'accounts/register.html', {'form': form})
        
        if form.is_valid():
            # Create user and mark verified immediately (OTP step removed)
            user = form.save(commit=False)
            user.is_active = True
            user.is_verified = True
            user.save()

            messages.success(request, 'Registration successful! You can now login.')
            return redirect('accounts:login')
        else:
            # Regenerate CAPTCHA on form error
            captcha_text, captcha_filename = CaptchaGenerator.generate_and_save(
                request.session.session_key
            )
            request.session['captcha_text'] = captcha_text
            request.session['captcha_filename'] = captcha_filename
    else:
        form = CitizenRegistrationForm()
    
    context = {
        'form': form,
        'captcha_image': request.session.get('captcha_filename', '')
    }
    return render(request, 'accounts/register.html', context)


def verify_otp(request):
    """
    OTP verification after registration
    """
    
    pending_user_id = request.session.get('pending_user_id')
    
    if not pending_user_id:
        messages.error(request, 'No pending verification found.')
        return redirect('accounts:register')
    
    try:
        user = Citizen.objects.get(id=pending_user_id)
    except Citizen.DoesNotExist:
        messages.error(request, 'Invalid user session.')
        return redirect('accounts:register')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        
        if form.is_valid():
            otp = form.cleaned_data['otp']
            
            if user.verify_otp(otp):
                # Clear session
                del request.session['pending_user_id']
                
                # Log the user in
                login(request, user)
                
                messages.success(request, 'Email verified successfully! You can now file complaints.')
                return redirect('complaints:dashboard')
            else:
                messages.error(request, 'Invalid or expired OTP. Please try again.')
    else:
        form = OTPVerificationForm()
    
    context = {
        'form': form,
        'email': user.email
    }
    return render(request, 'accounts/verify_otp.html', context)


def resend_otp(request):
    """
    Resend OTP to user
    """
    
    pending_user_id = request.session.get('pending_user_id')
    
    if not pending_user_id:
        messages.error(request, 'No pending verification found.')
        return redirect('accounts:register')
    
    try:
        user = Citizen.objects.get(id=pending_user_id)
        
        # Generate new OTP
        otp = user.generate_otp()
        
        # Send OTP via email
        send_mail(
            subject='MCMS - Email Verification OTP (Resend)',
            message=f'Your new OTP for email verification is: {otp}\n\nThis OTP is valid for 10 minutes.\n\nMunicipal Complaint Management System',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        messages.success(request, 'OTP resent successfully! Check your email.')
    
    except Citizen.DoesNotExist:
        messages.error(request, 'Invalid user session.')
        return redirect('accounts:register')
    except Exception as e:
        messages.error(request, 'Error sending OTP. Please try again.')
    
    return redirect('accounts:login')


def citizen_login(request):
    """
    Citizen login with CAPTCHA verification
    """
    
    # Generate CAPTCHA for GET request
    if request.method == 'GET':
        if not request.session.session_key:
            request.session.create()
        
        captcha_text, captcha_filename = CaptchaGenerator.generate_and_save(
            request.session.session_key
        )
        request.session['captcha_text'] = captcha_text
        request.session['captcha_filename'] = captcha_filename
    
    if request.method == 'POST':
        form = CitizenLoginForm(request, data=request.POST)
        
        # Verify CAPTCHA
        captcha_input = request.POST.get('captcha_input', '')
        captcha_stored = request.session.get('captcha_text', '')
        
        if captcha_input.upper() != captcha_stored.upper():
            messages.error(request, 'Invalid CAPTCHA. Please try again.')
            
            # Regenerate CAPTCHA
            captcha_text, captcha_filename = CaptchaGenerator.generate_and_save(
                request.session.session_key
            )
            request.session['captcha_text'] = captcha_text
            request.session['captcha_filename'] = captcha_filename
            
            return render(request, 'accounts/login.html', {'form': form})
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        # Log login attempt
        ip_address = get_client_ip(request)
        LoginAttempt.objects.create(
            username=username,
            ip_address=ip_address,
            success=user is not None
        )
        
        if user is not None:
            # OTP/email verification removed — allow login immediately
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_page = request.GET.get('next', 'complaints:dashboard')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
            
            # Regenerate CAPTCHA
            captcha_text, captcha_filename = CaptchaGenerator.generate_and_save(
                request.session.session_key
            )
            request.session['captcha_text'] = captcha_text
            request.session['captcha_filename'] = captcha_filename
    else:
        form = CitizenLoginForm()
    
    context = {
        'form': form,
        'captcha_image': request.session.get('captcha_filename', '')
    }
    return render(request, 'accounts/login.html', context)


@login_required
def citizen_logout(request):
    """
    Citizen logout
    """
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


def refresh_captcha(request):
    """
    AJAX endpoint to refresh CAPTCHA
    """
    if not request.session.session_key:
        request.session.create()
    
    captcha_text, captcha_filename = CaptchaGenerator.generate_and_save(
        request.session.session_key
    )
    request.session['captcha_text'] = captcha_text
    request.session['captcha_filename'] = captcha_filename
    
    from django.http import JsonResponse
    return JsonResponse({
        'captcha_image': f'/media/captcha/{captcha_filename}'
    })
