# Deployment Guide

This guide covers deploying the Library Management System to various platforms.

## Production Checklist

Before deploying to production, ensure:

- [ ] `DEBUG = False` in settings
- [ ] Proper `SECRET_KEY` set
- [ ] Database configured (PostgreSQL recommended)
- [ ] Static files collected
- [ ] Media files storage configured
- [ ] HTTPS enabled
- [ ] Environment variables set
- [ ] Backup strategy implemented

## Environment Setup

### Production Settings

Create a separate settings file for production:

```python
# settings/production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = '/var/www/library-lms/staticfiles'
MEDIA_ROOT = '/var/www/library-lms/media'

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Deployment Options

### 1. Traditional Server (Ubuntu/CentOS)

#### Prerequisites
```bash
sudo apt update
sudo apt install python3 python3-pip postgresql nginx supervisor
```

#### Setup Application
```bash
# Create application directory
sudo mkdir -p /var/www/library-lms
cd /var/www/library-lms

# Clone repository
sudo git clone <repository-url> .
sudo chown -R www-data:www-data /var/www/library-lms

# Create virtual environment
sudo -u www-data python3 -m venv venv
sudo -u www-data venv/bin/pip install -r requirements.txt

# Install additional production packages
sudo -u www-data venv/bin/pip install gunicorn psycopg2-binary
```

#### Database Setup
```bash
sudo -u postgres createuser libraryuser
sudo -u postgres createdb librarydb -O libraryuser
sudo -u postgres psql -c "ALTER USER libraryuser PASSWORD 'secure_password';"
```

#### Environment Configuration
```bash
# Create .env file
sudo -u www-data nano /var/www/library-lms/.env
```

Add:
```env
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
DB_NAME=librarydb
DB_USER=libraryuser
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

#### Run Migrations
```bash
cd /var/www/library-lms
sudo -u www-data venv/bin/python manage.py migrate
sudo -u www-data venv/bin/python manage.py collectstatic --noinput
sudo -u www-data venv/bin/python manage.py createsuperuser
```

#### Gunicorn Configuration
Create `/etc/supervisor/conf.d/library-lms.conf`:
```ini
[program:library-lms]
command=/var/www/library-lms/venv/bin/gunicorn library_management_system.wsgi:application --bind 127.0.0.1:8000
directory=/var/www/library-lms
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/library-lms.log
```

#### Nginx Configuration
Create `/etc/nginx/sites-available/library-lms`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/library-lms;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        root /var/www/library-lms;
        expires 30d;
        add_header Cache-Control "public";
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/library-lms /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
```

### 2. Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "library_management_system.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: librarydb
      POSTGRES_USER: libraryuser
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DB_NAME=librarydb
      - DB_USER=libraryuser
      - DB_PASSWORD=secure_password
      - DB_HOST=db
      - DB_PORT=5432
    depends_on:
      - db
    volumes:
      - ./media:/app/media
      - ./staticfiles:/app/staticfiles

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./staticfiles:/var/www/static
      - ./media:/var/www/media
    depends_on:
      - web

volumes:
  postgres_data:
```

Deploy with:
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 3. Cloud Platforms

#### Heroku
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create library-lms-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

#### AWS EC2 with RDS
Similar to traditional server setup but using AWS RDS for PostgreSQL:

```python
# Production settings for AWS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'librarydb',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': 'library-db.xxxx.us-east-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}

# Use S3 for static/media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.StaticS3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'library-lms-static'
```

## Monitoring and Maintenance

### Logging
```python
# Add to production settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/library-lms/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Backup Strategy
```bash
# Database backup script
#!/bin/bash
BACKUP_DIR="/var/backups/library-lms"
DATE=$(date +"%Y%m%d_%H%M%S")

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U libraryuser librarydb > $BACKUP_DIR/db_backup_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /var/www/library-lms/media

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Performance Optimization
```python
# Add to production settings

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 60

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Session storage
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### SSL/TLS Certificate
Use Let's Encrypt for free SSL certificates:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Security Hardening

1. **Firewall Configuration**
   ```bash
   sudo ufw allow OpenSSH
   sudo ufw allow 'Nginx Full'
   sudo ufw enable
   ```

2. **Regular Updates**
   ```bash
   sudo apt update && sudo apt upgrade
   pip install -r requirements.txt --upgrade
   ```

3. **Security Headers**
   Add to Nginx configuration:
   ```nginx
   add_header X-Frame-Options "SAMEORIGIN" always;
   add_header X-XSS-Protection "1; mode=block" always;
   add_header X-Content-Type-Options "nosniff" always;
   ```

4. **Database Security**
   - Use strong passwords
   - Limit database access to application server only
   - Regular security updates

## Troubleshooting

### Common Issues

1. **Static files not loading**
   ```bash
   python manage.py collectstatic --clear
   ```

2. **Database connection errors**
   - Check database credentials
   - Verify database server is running
   - Check firewall settings

3. **Permission errors**
   ```bash
   sudo chown -R www-data:www-data /var/www/library-lms
   sudo chmod -R 755 /var/www/library-lms
   ```

4. **502 Bad Gateway**
   - Check Gunicorn is running
   - Verify Nginx configuration
   - Check application logs

### Log Locations
- Application logs: `/var/log/library-lms.log`
- Nginx logs: `/var/log/nginx/error.log`
- System logs: `/var/log/syslog`

## Support

For deployment issues:
1. Check the logs first
2. Verify all prerequisites are installed
3. Ensure environment variables are set correctly
4. Test database connectivity
5. Create an issue on GitHub with detailed error information