@echo off
echo ========================================
echo MCMS - Municipal Complaint Management System
echo Quick Setup Script for Windows
echo ========================================
echo.

echo Step 1: Installing Django and Pillow...
pip install django pillow
echo.

echo Step 2: Running database migrations...
python manage.py makemigrations
python manage.py migrate
echo.

echo Step 3: Creating directories...
mkdir media\complaints 2>nul
mkdir media\captcha 2>nul
mkdir staticfiles 2>nul
echo Directories created!
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Create superuser: python manage.py createsuperuser
echo 2. Load departments (see README.md Step 6)
echo 3. Run server: python manage.py runserver
echo.
echo Then visit: http://127.0.0.1:8000/
echo ========================================
pause
