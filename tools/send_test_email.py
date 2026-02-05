#!/usr/bin/env python
"""
Send a test email using Django email configuration.
Usage: python tools/send_test_email.py recipient@example.com

This uses the active Django settings: if SMTP env vars are set, it will attempt to send via SMTP.
Otherwise it will write to the `emails/` folder (file backend).
"""
import os
import sys
from pathlib import Path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python tools/send_test_email.py recipient@example.com')
        sys.exit(1)

    recipient = sys.argv[1]

    # Ensure Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcms_config.settings')
    import django
    django.setup()

    from django.conf import settings
    from django.core.mail import send_mail

    subject = 'MCMS - Test Email'
    message = 'This is a test email from MCMS. If you received this, SMTP is configured correctly.'
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(subject, message, from_email, [recipient], fail_silently=False)
        print('Test email sent (or written to file backend).')
        if getattr(settings, 'EMAIL_FILE_PATH', None):
            print(f"Email files are saved to: {settings.EMAIL_FILE_PATH}")
    except Exception as e:
        print('Error sending test email:')
        print(str(e))
        sys.exit(2)
