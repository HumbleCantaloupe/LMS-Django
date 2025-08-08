import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from books.models import Book


class Command(BaseCommand):
    help = 'Add cover images to existing books'

    def handle(self, *args, **options):
        # Book cover URLs from Open Library or other free sources
        book_covers = {
            'Harry Potter and the Philosopher\'s Stone': 'https://covers.openlibrary.org/b/isbn/9780747532699-L.jpg',
            '1984': 'https://covers.openlibrary.org/b/isbn/9780452284234-L.jpg',
            'Pride and Prejudice': 'https://covers.openlibrary.org/b/isbn/9780141439518-L.jpg',
            'The Shining': 'https://covers.openlibrary.org/b/isbn/9780385121675-L.jpg',
            'And Then There Were None': 'https://covers.openlibrary.org/b/isbn/9780062073488-L.jpg',
            'Foundation': 'https://covers.openlibrary.org/b/isbn/9780553293357-L.jpg',
            'The Adventures of Tom Sawyer': 'https://covers.openlibrary.org/b/isbn/9780486400778-L.jpg',
            'To the Lighthouse': 'https://covers.openlibrary.org/b/isbn/9780156907392-L.jpg',
            'A Tale of Two Cities': 'https://covers.openlibrary.org/b/isbn/9780486406510-L.jpg',
            'War and Peace': 'https://covers.openlibrary.org/b/isbn/9780140447934-L.jpg',
        }

        for book_title, cover_url in book_covers.items():
            try:
                book = Book.objects.get(title=book_title)
                
                if book.cover_image:
                    self.stdout.write(f'Book "{book_title}" already has a cover image.')
                    continue
                
                self.stdout.write(f'Downloading cover for "{book_title}"...')
                
                # Download the image
                response = requests.get(cover_url, timeout=10)
                response.raise_for_status()
                
                # Create filename
                filename = f"{book.title.replace(' ', '_').replace('\'', '').lower()}.jpg"
                
                # Save the image to the book
                book.cover_image.save(
                    filename,
                    ContentFile(response.content),
                    save=True
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully added cover image for "{book_title}"')
                )
                
            except Book.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Book "{book_title}" not found in database.')
                )
            except requests.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to download cover for "{book_title}": {e}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing "{book_title}": {e}')
                )

        self.stdout.write(self.style.SUCCESS('Book cover update completed!'))
