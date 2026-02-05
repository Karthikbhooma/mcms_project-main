@echo off
echo ========================================
echo MCMS - AUTOMATED SETUP SCRIPT
echo ========================================
echo.

echo [1/8] Installing Django and Pillow...
pip install django pillow
echo.

echo [2/8] Creating migration files for accounts app...
python manage.py makemigrations accounts
echo.

echo [3/8] Creating migration files for departments app...
python manage.py makemigrations departments
echo.

echo [4/8] Creating migration files for complaints app...
python manage.py makemigrations complaints
echo.

echo [5/8] Creating migration files for adminpanel app...
python manage.py makemigrations adminpanel
echo.

echo [6/8] Running all migrations...
python manage.py migrate
echo.

echo [7/8] Creating media directories...
mkdir media\complaints 2>nul
mkdir media\captcha 2>nul
echo Directories created!
echo.

echo [8/8] Running system check...
python manage.py check
echo.

echo ========================================
echo ✅ SETUP COMPLETE!
echo ========================================
echo.
echo NEXT STEPS:
echo 1. Create superuser:
echo    python manage.py createsuperuser
echo.
echo 2. Load departments (see TROUBLESHOOTING_GUIDE.txt)
echo.
echo 3. Run server:
echo    python manage.py runserver
echo.
echo Then visit: http://127.0.0.1:8000/
echo ========================================
pause
