#!/bin/bash

# Quick start script for hackathon backend

echo "🚀 Starting Django Backend..."
echo ""

# Activate virtual environment
source .venv/bin/activate

# Check if migrations are up to date
echo "📊 Checking database status..."
python manage.py makemigrations --check --dry-run 2>&1 | grep -q "No changes detected" || {
    echo "⚠️  New migrations detected. Running migrations..."
    python manage.py makemigrations
    python manage.py migrate
}

# Run the development server
echo ""
echo "✅ Backend is ready!"
echo "📡 API will be available at: http://localhost:8000/api/"
echo "🔐 Admin panel at: http://localhost:8000/admin/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver
