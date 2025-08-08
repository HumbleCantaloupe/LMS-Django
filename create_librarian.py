#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management_system.settings')

django.setup()

from accounts.models import User

username = 'Marrow'
email = 'marrow@library.com'
password = 'Marrow'

if User.objects.filter(username=username).exists():
    print(f"User '{username}' already exists!")
    user = User.objects.get(username=username)
else:
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"Librarian '{username}' created successfully!")

user.is_staff = True
user.is_superuser = True
user.user_type = 'librarian'
user.save()

print(f"Username: {user.username}")
print(f"Email: {user.email}")
print(f"Is Staff: {user.is_staff}")
print(f"Is Superuser: {user.is_superuser}")
print(f"Date Joined: {user.date_joined}")
