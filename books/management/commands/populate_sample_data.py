from django.core.management.base import BaseCommand
from django.db import transaction
from books.models import Author, Publisher, Category, Book, BookCopy
from library_branches.models import LibraryBranch, LibrarySection
from accounts.models import User
from datetime import date, datetime
import random

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('Creating sample data...')
            
            # Create library branch
            branch, created = LibraryBranch.objects.get_or_create(
                name='Main Library',
                defaults={
                    'code': 'MAIN',
                    'address': '123 Library Street, City',
                    'phone_number': '+960-123-4567',
                    'email': 'main@library.com',
                    'manager_name': 'John Smith',
                    'established_date': date(2000, 1, 1),
                    'total_capacity': 10000,
                    'is_active': True,
                }
            )
            
            # Create sections
            sections_data = [
                ('Fiction', 'fiction', 1, 'A1', 'A20', 500),
                ('Non-Fiction', 'non_fiction', 1, 'B1', 'B20', 400),
                ('Science', 'study_materials', 2, 'C1', 'C15', 300),
                ('History', 'non_fiction', 2, 'D1', 'D10', 200),
                ('Children', 'children', 1, 'E1', 'E15', 350),
            ]
            
            sections = {}
            for name, section_type, floor, start_shelf, end_shelf, capacity in sections_data:
                section, created = LibrarySection.objects.get_or_create(
                    name=name,
                    branch=branch,
                    defaults={
                        'section_type': section_type,
                        'floor_number': floor,
                        'shelf_range_start': start_shelf,
                        'shelf_range_end': end_shelf,
                        'capacity': capacity,
                        'description': f'{name} books section',
                    }
                )
                sections[name] = section
            
            # Create categories
            categories_data = [
                ('Fiction', 'Fictional works'),
                ('Science Fiction', 'Science fiction novels'),
                ('Mystery', 'Mystery and thriller books'),
                ('Biography', 'Biographical works'),
                ('Technology', 'Technology and programming'),
                ('History', 'Historical books'),
                ('Children', 'Books for children'),
            ]
            
            categories = {}
            for name, description in categories_data:
                category, created = Category.objects.get_or_create(
                    name=name,
                    defaults={'description': description}
                )
                categories[name] = category
            
            # Create publishers
            publishers_data = [
                ('Penguin Random House', 'New York, USA'),
                ('HarperCollins', 'London, UK'),
                ('Simon & Schuster', 'New York, USA'),
                ('Macmillan Publishers', 'London, UK'),
                ("O'Reilly Media", 'Sebastopol, USA'),
            ]
            
            publishers = {}
            for name, address in publishers_data:
                publisher, created = Publisher.objects.get_or_create(
                    name=name,
                    defaults={'address': address}
                )
                publishers[name] = publisher
            
            # Create authors
            authors_data = [
                ('J.K.', 'Rowling', 'British author, best known for Harry Potter series'),
                ('George', 'Orwell', 'English novelist and journalist'),
                ('Jane', 'Austen', 'English novelist'),
                ('Stephen', 'King', 'American author of horror and fantasy'),
                ('Agatha', 'Christie', 'British crime novelist'),
                ('Isaac', 'Asimov', 'American science fiction writer'),
                ('Mark', 'Twain', 'American writer and humorist'),
                ('Virginia', 'Woolf', 'English writer and modernist'),
                ('Charles', 'Dickens', 'English writer and social critic'),
                ('Leo', 'Tolstoy', 'Russian writer'),
            ]
            
            authors = {}
            for first_name, last_name, biography in authors_data:
                author, created = Author.objects.get_or_create(
                    first_name=first_name,
                    last_name=last_name,
                    defaults={'biography': biography}
                )
                authors[f'{first_name} {last_name}'] = author
            
            # Create books
            books_data = [
                {
                    'isbn': '9780747532699',
                    'title': "Harry Potter and the Philosopher's Stone",
                    'authors': ['J.K. Rowling'],
                    'publisher': 'Penguin Random House',
                    'publication_date': date(1997, 6, 26),
                    'pages': 223,
                    'category': 'Fiction',
                    'description': 'The first book in the Harry Potter series.',
                    'price': 15.99
                },
                {
                    'isbn': '9780451524935',
                    'title': '1984',
                    'authors': ['George Orwell'],
                    'publisher': 'Penguin Random House',
                    'publication_date': date(1949, 6, 8),
                    'pages': 328,
                    'category': 'Fiction',
                    'description': 'A dystopian social science fiction novel.',
                    'price': 12.99
                },
                {
                    'isbn': '9780141439518',
                    'title': 'Pride and Prejudice',
                    'authors': ['Jane Austen'],
                    'publisher': 'Penguin Random House',
                    'publication_date': date(1813, 1, 28),
                    'pages': 279,
                    'category': 'Fiction',
                    'description': 'A romantic novel of manners.',
                    'price': 11.99
                },
                {
                    'isbn': '9780307277671',
                    'title': 'The Shining',
                    'authors': ['Stephen King'],
                    'publisher': 'Penguin Random House',
                    'publication_date': date(1977, 1, 28),
                    'pages': 447,
                    'category': 'Fiction',
                    'description': 'A horror novel about the Overlook Hotel.',
                    'price': 14.99
                },
                {
                    'isbn': '9780062073488',
                    'title': 'And Then There Were None',
                    'authors': ['Agatha Christie'],
                    'publisher': 'HarperCollins',
                    'publication_date': date(1939, 11, 6),
                    'pages': 264,
                    'category': 'Mystery',
                    'description': 'A mystery novel about ten strangers on an island.',
                    'price': 13.99
                },
                {
                    'isbn': '9780553293357',
                    'title': 'Foundation',
                    'authors': ['Isaac Asimov'],
                    'publisher': 'Penguin Random House',
                    'publication_date': date(1951, 1, 1),
                    'pages': 244,
                    'category': 'Science Fiction',
                    'description': 'The first novel in the Foundation series.',
                    'price': 13.99
                },
                {
                    'isbn': '9780486280615',
                    'title': 'The Adventures of Tom Sawyer',
                    'authors': ['Mark Twain'],
                    'publisher': 'Penguin Random House',
                    'publication_date': date(1876, 1, 1),
                    'pages': 274,
                    'category': 'Children',
                    'description': 'Adventures of a young boy in Missouri.',
                    'price': 9.99
                },
                {
                    'isbn': '9780156907392',
                    'title': 'To the Lighthouse',
                    'authors': ['Virginia Woolf'],
                    'publisher': 'HarperCollins',
                    'publication_date': date(1927, 5, 5),
                    'pages': 209,
                    'category': 'Fiction',
                    'description': 'A modernist novel about the Ramsay family.',
                    'price': 12.99
                },
                {
                    'isbn': '9780486415864',
                    'title': 'A Tale of Two Cities',
                    'authors': ['Charles Dickens'],
                    'publisher': 'Penguin Random House',
                    'publication_date': date(1859, 11, 26),
                    'pages': 341,
                    'category': 'History',
                    'description': 'A historical novel set during the French Revolution.',
                    'price': 11.99
                },
                {
                    'isbn': '9780486437064',
                    'title': 'War and Peace',
                    'authors': ['Leo Tolstoy'],
                    'publisher': 'Penguin Random House',
                    'publication_date': date(1869, 1, 1),
                    'pages': 1225,
                    'category': 'History',
                    'description': 'Epic novel about Russian society during the Napoleonic era.',
                    'price': 18.99
                },
            ]
            
            # Create books and book copies
            for book_data in books_data:
                book, created = Book.objects.get_or_create(
                    isbn=book_data['isbn'],
                    defaults={
                        'title': book_data['title'],
                        'publisher': publishers[book_data['publisher']],
                        'publication_date': book_data['publication_date'],
                        'pages': book_data['pages'],
                        'category': categories[book_data['category']],
                        'description': book_data['description'],
                        'price': book_data['price'],
                        'is_active': True,
                    }
                )
                
                # Add authors to the book
                for author_name in book_data['authors']:
                    book.authors.add(authors[author_name])
                
                # Create multiple copies of each book
                for i in range(random.randint(2, 5)):
                    copy_number = f"{book.isbn}-{i+1:03d}"
                    barcode = f"BC{book.isbn}{i+1:03d}"
                    book_copy, created = BookCopy.objects.get_or_create(
                        book=book,
                        copy_number=copy_number,
                        defaults={
                            'branch': branch,
                            'section': sections[random.choice(['Fiction', 'Science', 'History', 'Children'])],
                            'barcode': barcode,
                            'status': 'available',
                            'condition': random.choice(['excellent', 'good', 'fair']),
                            'acquisition_date': date(2020 + random.randint(0, 4), random.randint(1, 12), random.randint(1, 28)),
                        }
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created sample data:\n'
                    f'- {Author.objects.count()} authors\n'
                    f'- {Publisher.objects.count()} publishers\n'
                    f'- {Category.objects.count()} categories\n'
                    f'- {Book.objects.count()} books\n'
                    f'- {BookCopy.objects.count()} book copies\n'
                    f'- {LibraryBranch.objects.count()} library branch(es)\n'
                    f'- {LibrarySection.objects.count()} sections'
                )
            )
