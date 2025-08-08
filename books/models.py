from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from decimal import Decimal
from django.urls import reverse

class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    biography = models.TextField(blank=True)
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Publisher(models.Model):
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    established_year = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent_category = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='subcategories'
    )

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def full_name(self):
        if self.parent_category:
            return f"{self.parent_category.name} > {self.name}"
        return self.name

class Book(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('dv', 'Dhivehi'),
        ('ar', 'Arabic'),
        ('hi', 'Hindi'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('other', 'Other'),
    ]

    FORMAT_CHOICES = [
        ('hardcover', 'Hardcover'),
        ('paperback', 'Paperback'),
        ('ebook', 'E-book'),
        ('audiobook', 'Audiobook'),
    ]

    isbn_validator = RegexValidator(
        regex=r'^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$',
        message='Enter a valid ISBN number.'
    )

    isbn = models.CharField(max_length=17, unique=True, validators=[isbn_validator])
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300, blank=True)
    authors = models.ManyToManyField(Author, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, blank=True, null=True)
    publication_date = models.DateField()
    edition = models.CharField(max_length=50, blank=True)
    pages = models.PositiveIntegerField()
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='paperback')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('books:detail', kwargs={'pk': self.pk})

    @property
    def author_list(self):
        return ", ".join([author.full_name for author in self.authors.all()])

    @property
    def available_copies_count(self):
        return self.book_copies.filter(status='available').count()

    @property
    def borrowed_copies_count(self):
        return self.book_copies.filter(status='borrowed').count()

    @property
    def total_copies_count(self):
        return self.book_copies.count()

class BookCopy(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Under Maintenance'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]

    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_copies')
    branch = models.ForeignKey('library_branches.LibraryBranch', on_delete=models.CASCADE, related_name='book_copies')
    section = models.ForeignKey('library_branches.LibrarySection', on_delete=models.SET_NULL, blank=True, null=True, related_name='book_copies')
    copy_number = models.CharField(max_length=50)
    barcode = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    acquisition_date = models.DateField()
    last_maintenance_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Book Copy'
        verbose_name_plural = 'Book Copies'
        ordering = ['book__title', 'copy_number']
        unique_together = [['book', 'branch', 'copy_number']]

    def __str__(self):
        return f"{self.book.title} - Copy {self.copy_number} ({self.branch.name})"

    @property
    def is_available(self):
        return self.status == 'available'

class BookReservation(models.Model):
    RESERVATION_TYPE_CHOICES = [
        ('regular', 'Regular Reservation'),
        ('priority', 'Priority Reservation'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    branch = models.ForeignKey('library_branches.LibraryBranch', on_delete=models.CASCADE, related_name='reservations')
    reservation_type = models.CharField(max_length=20, choices=RESERVATION_TYPE_CHOICES, default='regular')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    reserved_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    fulfilled_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['reserved_at']
        unique_together = [['user', 'book', 'status']]

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expires_at < timezone.now() and self.status == 'active'
