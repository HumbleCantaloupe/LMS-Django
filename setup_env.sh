#!/bin/bash
# Django LMS Development Environment Setup

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo "Virtual environment activated. Python path: $(which python)"
else
    echo "Virtual environment not found. Please create one with: python -m venv venv"
fi

# Show current directory
echo "Current directory: $(pwd)"

# Show Django project status
if [ -f "manage.py" ]; then
    echo "Django project detected. Available commands:"
    echo "  python manage.py runserver    - Start development server"
    echo "  python manage.py shell        - Open Django shell"
    echo "  python manage.py check        - Check for issues"
    echo "  python manage.py migrate      - Apply migrations"
    echo "  python manage.py makemigrations - Create new migrations"
else
    echo "manage.py not found. Are you in the Django project directory?"
fi
