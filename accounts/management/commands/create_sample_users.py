from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User
from datetime import date, datetime, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create sample users for testing'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('Creating sample users...')
            
            # Sample users data
            users_data = [
                {
                    'username': 'librarian1',
                    'email': 'librarian@library.com',
                    'first_name': 'Sarah',
                    'last_name': 'Johnson',
                    'user_type': 'librarian',
                    'phone_number': '+960-111-1111',
                    'is_staff': True,
                    'password': 'library123'
                },
                {
                    'username': 'member1',
                    'email': 'john.doe@email.com',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'user_type': 'member',
                    'phone_number': '+960-222-2222',
                    'date_of_birth': date(1990, 5, 15),
                    'address': '123 Main Street, City',
                    'password': 'member123'
                },
                {
                    'username': 'member2',
                    'email': 'jane.smith@email.com',
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'user_type': 'member',
                    'phone_number': '+960-333-3333',
                    'date_of_birth': date(1985, 8, 22),
                    'address': '456 Oak Avenue, City',
                    'password': 'member123'
                },
                {
                    'username': 'member3',
                    'email': 'mike.wilson@email.com',
                    'first_name': 'Mike',
                    'last_name': 'Wilson',
                    'user_type': 'member',
                    'phone_number': '+960-444-4444',
                    'date_of_birth': date(1995, 12, 3),
                    'address': '789 Pine Street, City',
                    'password': 'member123'
                },
                {
                    'username': 'admin1',
                    'email': 'admin@library.com',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'user_type': 'admin',
                    'phone_number': '+960-555-5555',
                    'is_staff': True,
                    'is_superuser': True,
                    'password': 'admin123'
                }
            ]
            
            created_count = 0
            for user_data in users_data:
                username = user_data['username']
                if not User.objects.filter(username=username).exists():
                    password = user_data.pop('password')
                    user = User.objects.create_user(**user_data)
                    user.set_password(password)
                    user.save()
                    created_count += 1
                    self.stdout.write(f'Created user: {username} ({user.get_user_type_display()})')
                else:
                    self.stdout.write(f'User {username} already exists, skipping...')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {created_count} users.\n'
                    f'Total users in system: {User.objects.count()}\n'
                    f'Test login credentials:\n'
                    f'- Librarian: librarian1 / library123\n'
                    f'- Member: member1 / member123\n'
                    f'- Admin: admin1 / admin123'
                )
            )
