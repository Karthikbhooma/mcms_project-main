#!/bin/bash

echo "========================================"
echo "MCMS - Municipal Complaint Management System"
echo "Quick Setup Script for Linux/Mac"
echo "========================================"
echo ""

echo "Step 1: Installing Django and Pillow..."
pip3 install django pillow
echo ""

echo "Step 2: Running database migrations..."
python3 manage.py makemigrations
python3 manage.py migrate
echo ""

echo "Step 3: Creating directories..."
mkdir -p media/complaints
mkdir -p media/captcha
mkdir -p staticfiles
echo "Directories created!"
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next Steps:"
echo "1. Create superuser: python3 manage.py createsuperuser"
echo "2. Load departments (see README.md Step 6)"
echo "3. Run server: python3 manage.py runserver"
echo ""
echo "Then visit: http://127.0.0.1:8000/"
echo "========================================"
