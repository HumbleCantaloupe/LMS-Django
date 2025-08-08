# Library Management System (LMS)

A comprehensive Django-based Library Management System designed for modern libraries. This system provides complete functionality for managing books, members, borrowing transactions, fines, and multiple library branches.

## Features

### 📚 Book Management
- Complete book catalog with ISBN, authors, publishers, categories
- Book copy tracking with barcode system
- Multi-format support (hardcover, paperback, ebook, audiobook)
- Advanced search and filtering capabilities
- Book reservation system with priority options

### 👥 User Management
- Multi-role user system (Members, Librarians, Administrators)
- Custom user profiles with reading preferences
- Library card number generation
- Membership management and renewals

### 🔄 Borrowing System
- Real-time book borrowing and return tracking
- Automatic due date calculation
- Book renewal system with configurable limits
- Overdue book detection and notifications

### 💰 Fine Management
- Automatic fine calculation for overdue books
- Multiple payment methods support
- Fine payment tracking and receipts
- Membership fee management

### 🏢 Branch Management
- Multiple library branch support
- Branch-specific book collections
- Operating hours management
- Section-wise book organization

### 📊 Reporting & Analytics
- Borrowing history and statistics
- Member activity reports
- Book popularity analytics
- Financial reports for fines and fees

## Technology Stack

- **Backend**: Django 5.2.5
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Authentication**: Django's built-in authentication system
- **File Storage**: Django's file handling for book covers and documents

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LMS-Django
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Load sample data (optional)**
   ```bash
   python manage.py loaddata fixtures/sample_data.json
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main application: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Configuration

### Environment Variables
Create a `.env` file in the project root with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=127.0.0.1,localhost

# Email settings (for notifications)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Library specific settings
MAX_BOOKS_PER_USER=5
DEFAULT_LOAN_PERIOD_DAYS=14
MAX_RENEWALS=2
FINE_PER_DAY=1.00
RESERVATION_EXPIRY_HOURS=24
```

### Library Settings
You can customize library-specific settings in `settings.py`:

```python
LIBRARY_SETTINGS = {
    'MAX_BOOKS_PER_USER': 5,
    'DEFAULT_LOAN_PERIOD_DAYS': 14,
    'MAX_RENEWALS': 2,
    'FINE_PER_DAY': 1.00,
    'RESERVATION_EXPIRY_HOURS': 24,
}
```

## Usage

### For Members
1. Register for a library account
2. Browse and search the book catalog
3. Reserve books or borrow available copies
4. Manage borrowings and renewals
5. View borrowing history and pay fines

### For Librarians
1. Manage book catalog (add, edit, remove books)
2. Handle book borrowing and return transactions
3. Manage member accounts
4. Process fine payments
5. Generate reports

### For Administrators
1. Full system access and configuration
2. Manage multiple library branches
3. User role management
4. System-wide reporting and analytics

## API Endpoints

The system provides REST API endpoints for integration:

- `/api/books/` - Book catalog management
- `/api/members/` - Member management
- `/api/borrowing/` - Borrowing transactions
- `/api/fines/` - Fine management
- `/api/reports/` - System reports

## Testing

Run the test suite:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test books
python manage.py test accounts
python manage.py test borrowing
```

## Development

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and add tests
3. Run tests: `python manage.py test`
4. Commit changes: `git commit -m "Add new feature"`
5. Push and create pull request

### Database Schema Updates
1. Make model changes
2. Generate migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in the `docs/` folder
- Contact the development team

## Changelog

### Version 1.0.0
- Initial release with core LMS functionality
- Multi-branch library support
- Complete borrowing system
- Fine management
- User authentication and profiles

---

**Library Management System** - Streamlining library operations with modern technology.