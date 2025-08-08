#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management_system.settings')

django.setup()

from accounts.models import User

try:
    if User.objects.filter(username='Marrow').exists():
        user = User.objects.get(username='Marrow')
        print(f"✅ User 'Marrow' already exists!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   User Type: {user.user_type}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")
    else:
        user = User.objects.create_user(
            username='Marrow',
            email='marrow@library.com',
            password='Marrow'
        )
        user.is_staff = True
        user.is_superuser = True
        user.user_type = 'librarian'
        user.save()
        
        print(f"✅ Librarian 'Marrow' created successfully!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   User Type: {user.user_type}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🔍 All librarians in the system:")
librarians = User.objects.filter(user_type__in=['librarian', 'admin'])
for lib in librarians:
    print(f"   - {lib.username} ({lib.email}) - {lib.get_user_type_display()}")
