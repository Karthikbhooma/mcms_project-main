#!/usr/bin/env python
"""
Utility to view OTP from email files
Helps extract OTP during development
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def view_latest_otp():
    """View the latest OTP email"""
    email_dir = Path(__file__).parent.parent / 'emails'
    
    if not email_dir.exists():
        print("❌ Email directory not found. Ensure registration completed.")
        return
    
    email_files = sorted(email_dir.glob('*'), key=os.path.getctime, reverse=True)
    
    if not email_files:
        print("❌ No email files found. Try registering again.")
        return
    
    latest_email = email_files[0]
    
    print(f"\n📧 Latest Email: {latest_email.name}\n")
    print("=" * 60)
    
    with open(latest_email, 'r') as f:
        content = f.read()
        print(content)
    
    print("=" * 60)
    
    # Extract OTP
    for line in content.split('\n'):
        if 'Your OTP' in line or 'OTP' in line and any(c.isdigit() for c in line):
            print(f"\n✅ OTP: {line.strip()}")

def list_all_otps():
    """List all OTP emails"""
    email_dir = Path(__file__).parent.parent / 'emails'
    
    if not email_dir.exists():
        print("❌ Email directory not found.")
        return
    
    email_files = sorted(email_dir.glob('*'), key=os.path.getctime, reverse=True)
    
    if not email_files:
        print("❌ No email files found.")
        return
    
    print(f"\n📧 Total Emails: {len(email_files)}\n")
    
    for idx, email_file in enumerate(email_files, 1):
        with open(email_file, 'r') as f:
            content = f.read()
            # Extract email address
            for line in content.split('\n'):
                if 'To:' in line:
                    print(f"{idx}. {email_file.name} → {line.strip()}")
                    break

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        list_all_otps()
    else:
        view_latest_otp()
