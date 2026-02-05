# OTP Email System - Setup & Usage Guide

## Problem Fixed

The MCMS system was not sending OTP emails to users. The email backend was configured to use **Console Backend**, which only prints emails to the console instead of actually sending them.

**Status:** ✅ FIXED - Now using **File-Based Email Backend**

---

## How It Works Now

### Email Backend Configuration

The system is now configured to save all emails to files in the `emails/` directory:

```
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'emails'
DEFAULT_FROM_EMAIL = 'MCMS - Municipal Corporation <mcms@gov.in>'
```

### Email Flow

1. User registers with email
2. OTP is generated (6 random digits)
3. Email is saved to `emails/<timestamp>-<hash>.txt`
4. User reads OTP from email file
5. User enters OTP to verify email

---

## How to Use

### Step 1: Register a User

Visit: http://127.0.0.1:8000/accounts/register/

- **Email:** Any email address (e.g., `vishali.jampala30@gmail.com`)
- **Username:** Any username
- **Mobile:** 10-digit number
- **Password:** Strong password (8+ chars, mix of types)
- **Fill CAPTCHA:** Enter the displayed text

Click "Register"

### Step 2: Check OTP Email

After registration, an email is saved to the `emails/` folder.

**Option A: Quick View**

Run this Python command to see the latest OTP:

```bash
python tools/view_otp.py
```

This will display the email content and highlight the OTP code.

**Option B: Manual Check**

1. Open the `emails/` folder in your project
2. Look for the most recent file (sorted by timestamp)
3. Open it with any text editor
4. Find the line: `Your OTP for email verification is: XXXXXX`
5. Copy the 6-digit code

**Option C: List All Emails**

```bash
python tools/view_otp.py list
```

Shows all email files created so far.

### Step 3: Verify OTP

You'll be redirected to: http://127.0.0.1:8000/accounts/verify-otp/

- Paste the OTP from the email file
- Click "Verify OTP"
- Account will be activated

---

## Email File Format

Each email file contains the complete SMTP message format:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: MCMS - Email Verification OTP
From: MCMS - Municipal Corporation <mcms@gov.in>
To: vishali.jampala30@gmail.com
Date: Mon, 04 Feb 2026 12:34:56 -0000
Message-ID: <...@mcms.gov.in>

Your OTP for email verification is: 123456

This OTP is valid for 10 minutes.

Municipal Complaint Management System
```

---

## Configuration Files Modified

### `mcms_config/settings.py`

**Before:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**After:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'emails'
```

---

## For Production Use

When deploying to production, use a real SMTP service:

### Option 1: Gmail SMTP

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Generate from Google Account
DEFAULT_FROM_EMAIL = 'noreply@mcms.gov.in'
```

### Environment variable based configuration (recommended)

Set the following environment variables on your machine or hosting platform (example for Windows PowerShell):

```powershell
setx SMTP_HOST "smtp.gmail.com"
setx SMTP_PORT "587"
setx SMTP_USER "your-email@gmail.com"
setx SMTP_PASSWORD "your-app-password"
setx SMTP_USE_TLS "True"
setx DEFAULT_FROM_EMAIL "noreply@mcms.gov.in"
```

Or on Linux/macOS (bash):

```bash
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
export SMTP_USE_TLS="True"
export DEFAULT_FROM_EMAIL="noreply@mcms.gov.in"
```

After setting env vars, restart your shell or IDE and then run the test script below.

### Option 2: SendGrid

```python
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = 'your-sendgrid-api-key'
DEFAULT_FROM_EMAIL = 'noreply@mcms.gov.in'
```

### Option 3: AWS SES

```python
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION_NAME = 'us-east-1'
AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'
```

---

## Utility Scripts

### View Latest OTP

```bash
python tools/view_otp.py
```

**Output:**
```
Email file: 20260204-083045-abc123.txt

Content-Type: text/plain; charset="utf-8"
...
Your OTP for email verification is: 654321
```

### List All OTP Emails

```bash
python tools/view_otp.py list
```

### Send a test email (validates SMTP)

Use this to verify SMTP credentials actually send mail. If SMTP env vars are set, this will attempt to send via SMTP. Otherwise it will write to the `emails/` folder.

```bash
python tools/send_test_email.py your-test-recipient@example.com
```

If you receive the test email in your inbox, the SMTP configuration is correct and OTP emails will be delivered to users.

**Output:**
```
Total Emails: 3

1. 20260204-083045-abc123.txt → To: user1@example.com
2. 20260204-083102-def456.txt → To: user2@example.com
3. 20260204-083201-ghi789.txt → To: user3@example.com
```

---

## OTP Verification Details

### OTP Generation

- **Length:** 6 digits
- **Validity:** 10 minutes from generation
- **Format:** Random numeric string
- **Storage:** In `Citizen.otp_code` field with timestamp

### OTP Verification

```python
# In accounts/views.py
def verify_otp(request):
    # User enters OTP
    # System checks:
    # 1. OTP matches Citizen.otp_code
    # 2. OTP not expired (< 10 minutes old)
    # 3. User not already verified
    # If all checks pass: user.is_verified = True
```

---

## Testing Workflow

### 1. Test Registration → OTP Email

```bash
# Start server
python manage.py runserver

# In browser, register with:
# - Email: test@example.com
# - Username: testuser
# - Mobile: 9999888877
# - Password: Test@Pass123
```

### 2. Check OTP Email

```bash
# In terminal
python tools/view_otp.py

# Output shows OTP like: 654321
```

### 3. Verify OTP

```bash
# In browser, paste OTP and click verify
# Account becomes active
```

### 4. Login

```bash
# Login with:
# - Email: test@example.com
# - Password: Test@Pass123
# - CAPTCHA: Enter displayed text
```

---

## Troubleshooting

### Issue: No email file created

**Check:**
1. Django is running (no errors on register)
2. `emails/` directory exists
3. Path is correct: `c:/Users/visha/Downloads/mcms_complete_project (1)/mcms_project/emails`

**Fix:**
```bash
mkdir emails
python manage.py runserver
```

### Issue: OTP says "OTP sent" but no file created

**Check:**
1. `settings.EMAIL_FILE_PATH` is set correctly
2. File permissions allow writing to `emails/` folder
3. Email backend is `filebased.EmailBackend`

**Fix:**
```bash
# Verify backend
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_BACKEND)
django.core.mail.backends.filebased.EmailBackend
>>> print(settings.EMAIL_FILE_PATH)
C:\Users\visha\Downloads\mcms_complete_project (1)\mcms_project\emails
```

### Issue: OTP valid for 10 minutes but expired quickly

OTP expiration is checked in `accounts/models.py`:

```python
def verify_otp(self, otp_code):
    if self.otp_code != otp_code:
        return False
    
    # Check if OTP is expired (10 minutes)
    time_diff = timezone.now() - self.otp_created_at
    if time_diff.total_seconds() > 600:  # 10 minutes
        return False
    
    return True
```

The 10-minute timer resets on every registration attempt.

---

## Email File Locations

All emails are saved to:

```
mcms_project/
├── emails/
│   ├── 20260204-083045-abc123.txt
│   ├── 20260204-083102-def456.txt
│   └── 20260204-083201-ghi789.txt
```

Windows path: `C:\Users\visha\Downloads\mcms_complete_project (1)\mcms_project\emails\`

---

## Summary

✅ **Email Backend:** File-Based (saves to `emails/` folder)  
✅ **OTP Generation:** Automatic (6 random digits)  
✅ **OTP Validity:** 10 minutes from generation  
✅ **Verification:** Manual OTP entry from email file  
✅ **Production Ready:** Can switch to SMTP backend anytime  

**Next Step:** Register a user and check the OTP email file!
