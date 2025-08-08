from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from books.models import Author, Publisher, Category, Book
from library_branches.models import LibraryBranch
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for testing the library system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create a test librarian if it doesn't exist
        if not User.objects.filter(username='librarian').exists():
            librarian = User.objects.create_user(
                username='librarian',
                email='librarian@library.com',
                password='testpass123',
                user_type='librarian',
                first_name='John',
                last_name='Librarian'
            )
            self.stdout.write(f'Created librarian: {librarian}')
        
        # Create a test member if it doesn't exist
        if not User.objects.filter(username='member').exists():
            member = User.objects.create_user(
                username='member',
                email='member@example.com',
                password='testpass123',
                user_type='member',
                first_name='Jane',
                last_name='Reader'
            )
            self.stdout.write(f'Created member: {member}')
        
        # Create sample authors
        authors_data = [
            ('J.K.', 'Rowling', 'British'),
            ('George', 'Orwell', 'British'),
            ('Harper', 'Lee', 'American'),
        ]
        
        for first_name, last_name, nationality in authors_data:
            author, created = Author.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                defaults={'nationality': nationality}
            )
            if created:
                self.stdout.write(f'Created author: {author}')
        
        # Create sample publishers
        publishers_data = ['Penguin Books', 'Random House', 'Harper Collins']
        for pub_name in publishers_data:
            publisher, created = Publisher.objects.get_or_create(name=pub_name)
            if created:
                self.stdout.write(f'Created publisher: {publisher}')
        
        # Create sample categories
        categories_data = ['Fiction', 'Non-Fiction', 'Science', 'History', 'Biography']
        for cat_name in categories_data:
            category, created = Category.objects.get_or_create(name=cat_name)
            if created:
                self.stdout.write(f'Created category: {category}')
        
        # Create sample library branch
        if not LibraryBranch.objects.filter(code='MAIN').exists():
            branch = LibraryBranch.objects.create(
                name='Main Library Branch',
                code='MAIN',
                address='123 Library Street, City',
                phone_number='+1234567890',
                email='main@library.com',
                manager_name='Library Manager',
                established_date='2020-01-01',
                total_capacity=1000
            )
            self.stdout.write(f'Created branch: {branch}')
        
        # Create a sample book
        if not Book.objects.filter(isbn='9780747532699').exists():
            book = Book.objects.create(
                isbn='9780747532699',
                title='Harry Potter and the Philosopher\'s Stone',
                publication_date='1997-06-26',
                pages=223,
                description='A young wizard\'s journey begins...',
                publisher=Publisher.objects.first(),
                category=Category.objects.filter(name='Fiction').first()
            )
            book.authors.set([Author.objects.filter(first_name='J.K.').first()])
            self.stdout.write(f'Created book: {book}')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
