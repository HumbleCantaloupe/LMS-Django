# Library Management System (LMS)

A Django-based Library Management System for managing books, members, borrowing, and fines.

## Features

- Book catalog management
- User authentication and profiles
- Borrowing and return system
- Fine management
- Library branch support
- Admin panel for management

## Technology Stack

- Django 5.2.5
- SQLite database
- Bootstrap 5 frontend
- Python 3.9+

## Quick Start

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd LMS-Django
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. **Run server**
   ```bash
   python manage.py runserver
   ```

4. **Access application**
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## License

MIT License