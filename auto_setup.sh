#!/bin/bash

echo "========================================"
echo "MCMS - AUTOMATED SETUP SCRIPT"
echo "========================================"
echo ""

echo "[1/8] Installing Django and Pillow..."
pip3 install django pillow
echo ""

echo "[2/8] Creating migration files for accounts app..."
python3 manage.py makemigrations accounts
echo ""

echo "[3/8] Creating migration files for departments app..."
python3 manage.py makemigrations departments
echo ""

echo "[4/8] Creating migration files for complaints app..."
python3 manage.py makemigrations complaints
echo ""

echo "[5/8] Creating migration files for adminpanel app..."
python3 manage.py makemigrations adminpanel
echo ""

echo "[6/8] Running all migrations..."
python3 manage.py migrate
echo ""

echo "[7/8] Creating media directories..."
mkdir -p media/complaints media/captcha
echo "Directories created!"
echo ""

echo "[8/8] Running system check..."
python3 manage.py check
echo ""

echo "========================================"
echo "✅ SETUP COMPLETE!"
echo "========================================"
echo ""
echo "NEXT STEPS:"
echo "1. Create superuser:"
echo "   python3 manage.py createsuperuser"
echo ""
echo "2. Load departments (see TROUBLESHOOTING_GUIDE.txt)"
echo ""
echo "3. Run server:"
echo "   python3 manage.py runserver"
echo ""
echo "Then visit: http://127.0.0.1:8000/"
echo "========================================"
