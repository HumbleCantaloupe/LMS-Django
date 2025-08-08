from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('member', 'Library Member'),
        ('librarian', 'Librarian'),
        ('admin', 'Administrator'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='member')
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    library_card_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    is_active_member = models.BooleanField(default=True)
    membership_date = models.DateTimeField(default=timezone.now)
    membership_expiry = models.DateTimeField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def is_librarian(self):
        return self.user_type in ['librarian', 'admin']
    
    @property
    def is_member(self):
        return self.user_type == 'member'
    
    def save(self, *args, **kwargs):
        if not self.library_card_number and self.user_type == 'member':
            # Generate library card number
            last_member = User.objects.filter(user_type='member').order_by('id').last()
            if last_member and last_member.library_card_number:
                last_number = int(last_member.library_card_number.replace('LIB', ''))
                self.library_card_number = f"LIB{last_number + 1:06d}"
            else:
                self.library_card_number = "LIB000001"
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    notification_preferences = models.JSONField(default=dict, blank=True)
    preferred_branch = models.ForeignKey(
        'library_branches.LibraryBranch', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='preferred_by_users'
    )
    reading_preferences = models.ManyToManyField(
        'books.Category', 
        blank=True, 
        related_name='interested_users'
    )
    privacy_settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('book_borrowed', 'Book Borrowed'),
        ('book_returned', 'Book Returned'),
        ('book_reserved', 'Book Reserved'),
        ('fine_paid', 'Fine Paid'),
        ('profile_updated', 'Profile Updated'),
        ('password_changed', 'Password Changed'),
        ('account_created', 'Account Created'),
        ('account_deactivated', 'Account Deactivated'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} at {self.timestamp}"
