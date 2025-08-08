from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class LibraryBranch(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    address = models.TextField()
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmailField()
    manager_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    established_date = models.DateField()
    total_capacity = models.PositiveIntegerField(help_text="Maximum number of books this branch can hold")
    wifi_available = models.BooleanField(default=True)
    parking_available = models.BooleanField(default=False)
    accessible_entrance = models.BooleanField(default=True)
    study_rooms = models.PositiveIntegerField(default=0)
    computer_stations = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def current_book_count(self):
        return self.book_copies.count()
    
    @property
    def available_books_count(self):
        return self.book_copies.filter(status='available').count()
    
    @property
    def capacity_percentage(self):
        if self.total_capacity > 0:
            return (self.current_book_count / self.total_capacity) * 100
        return 0

class LibrarySection(models.Model):
    SECTION_TYPE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('reference', 'Reference'),
        ('periodicals', 'Periodicals'),
        ('children', 'Children\'s Section'),
        ('young_adult', 'Young Adult'),
        ('local_authors', 'Local Authors'),
        ('digital', 'Digital Collection'),
        ('rare_books', 'Rare Books'),
        ('study_materials', 'Study Materials'),
    ]
    
    branch = models.ForeignKey(LibraryBranch, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=100)
    section_type = models.CharField(max_length=20, choices=SECTION_TYPE_CHOICES)
    floor_number = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    shelf_range_start = models.CharField(max_length=10, help_text="Starting shelf identifier")
    shelf_range_end = models.CharField(max_length=10, help_text="Ending shelf identifier")
    is_restricted = models.BooleanField(default=False, help_text="Requires special permission to access")
    temperature_controlled = models.BooleanField(default=False)
    security_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Security'),
            ('medium', 'Medium Security'),
            ('high', 'High Security'),
        ],
        default='low'
    )
    capacity = models.PositiveIntegerField(help_text="Maximum number of books in this section")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['branch', 'floor_number', 'name']
        unique_together = [['branch', 'name']]
    
    def __str__(self):
        return f"{self.branch.name} - {self.name} (Floor {self.floor_number})"
    
    @property
    def current_book_count(self):
        return self.book_copies.count()
    
    @property
    def capacity_percentage(self):
        if self.capacity > 0:
            return (self.current_book_count / self.capacity) * 100
        return 0

class BranchOperatingHours(models.Model):
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    branch = models.ForeignKey(LibraryBranch, on_delete=models.CASCADE, related_name='operating_hours')
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_closed = models.BooleanField(default=False)
    special_hours_note = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['branch', 'weekday']
        unique_together = [['branch', 'weekday']]
    
    def __str__(self):
        if self.is_closed:
            return f"{self.branch.name} - {self.get_weekday_display()}: Closed"
        return f"{self.branch.name} - {self.get_weekday_display()}: {self.opening_time} - {self.closing_time}"
    
    @property
    def is_open_now(self):
        if self.is_closed:
            return False
        
        current_time = timezone.now().time()
        current_weekday = timezone.now().weekday()
        
        return (self.weekday == current_weekday and 
                self.opening_time <= current_time <= self.closing_time)
