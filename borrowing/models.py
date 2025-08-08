from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

class BorrowTransaction(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
        ('renewed', 'Renewed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrow_transactions')
    book_copy = models.ForeignKey('books.BookCopy', on_delete=models.CASCADE, related_name='borrow_transactions')
    librarian_issued = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='issued_transactions'
    )
    librarian_returned = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='returned_transactions'
    )
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    renewal_count = models.PositiveIntegerField(default=0)
    max_renewals_allowed = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-borrowed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.book_copy.book.title} ({self.status})"
    
    @property
    def is_overdue(self):
        if self.status in ['returned', 'lost']:
            return False
        return timezone.now() > self.due_date
    
    @property
    def days_overdue(self):
        if not self.is_overdue:
            return 0
        return (timezone.now().date() - self.due_date.date()).days
    
    @property
    def days_until_due(self):
        """Returns the number of days until the book is due"""
        if self.status in ['returned', 'lost']:
            return 0
        days_diff = (self.due_date.date() - timezone.now().date()).days
        return max(0, days_diff)
    
    @property
    def borrow_date(self):
        """Returns borrow date for template compatibility"""
        return self.borrowed_at.date() if self.borrowed_at else None
    
    @property
    def can_renew(self):
        return (self.status == 'active' and 
                self.renewal_count < self.max_renewals_allowed and 
                not self.is_overdue)
    
    @property
    def fine_amount(self):
        if not self.is_overdue:
            return Decimal('0.00')
        
        from django.conf import settings
        fine_per_day = getattr(settings, 'LIBRARY_SETTINGS', {}).get('FINE_PER_DAY', 1.00)
        return Decimal(str(fine_per_day)) * self.days_overdue
    
    def renew(self, librarian=None):
        if not self.can_renew:
            raise ValueError("This transaction cannot be renewed")
        
        loan_period = getattr(settings, 'LIBRARY_SETTINGS', {}).get('DEFAULT_LOAN_PERIOD_DAYS', 14)
        self.due_date = timezone.now() + timedelta(days=loan_period)
        self.renewal_count += 1
        self.status = 'renewed'
        if librarian:
            self.librarian_issued = librarian
        self.save()
        
        # Log the renewal
        BorrowingHistory.objects.create(
            user=self.user,
            book=self.book_copy.book,
            branch=self.book_copy.branch,
            borrowed_date=self.borrowed_at,
            renewal_count=self.renewal_count,
            action='renewed'
        )

class ReturnTransaction(models.Model):
    CONDITION_CHOICES = [
        ('excellent', 'Excellent Condition'),
        ('good', 'Good Condition'),
        ('fair', 'Fair Condition'),
        ('poor', 'Poor Condition'),
        ('damaged', 'Damaged'),
        ('lost', 'Lost'),
    ]
    
    borrow_transaction = models.OneToOneField(
        BorrowTransaction, 
        on_delete=models.CASCADE, 
        related_name='return_details'
    )
    librarian = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='processed_returns'
    )
    returned_at = models.DateTimeField(auto_now_add=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    damage_description = models.TextField(blank=True)
    damage_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    late_fine = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_penalty = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-returned_at']
    
    def __str__(self):
        return f"Return: {self.borrow_transaction.user.username} - {self.borrow_transaction.book_copy.book.title}"
    
    def save(self, *args, **kwargs):
        # Calculate total penalty
        self.total_penalty = self.damage_fee + self.late_fine
        super().save(*args, **kwargs)
        
        # Update the borrow transaction
        self.borrow_transaction.status = 'returned'
        self.borrow_transaction.returned_at = self.returned_at
        self.borrow_transaction.librarian_returned = self.librarian
        self.borrow_transaction.save()
        
        # Update book copy status
        self.borrow_transaction.book_copy.status = 'available'
        if self.condition in ['damaged', 'lost']:
            self.borrow_transaction.book_copy.status = self.condition
        self.borrow_transaction.book_copy.save()
        
        # Create history record
        BorrowingHistory.objects.create(
            user=self.borrow_transaction.user,
            book=self.borrow_transaction.book_copy.book,
            branch=self.borrow_transaction.book_copy.branch,
            borrowed_date=self.borrow_transaction.borrowed_at,
            returned_date=self.returned_at,
            days_borrowed=(self.returned_at.date() - self.borrow_transaction.borrowed_at.date()).days,
            was_overdue=self.borrow_transaction.is_overdue,
            fine_paid=self.total_penalty,
            renewal_count=self.borrow_transaction.renewal_count,
            action='returned'
        )

class BorrowingHistory(models.Model):
    ACTION_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('renewed', 'Renewed'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrowing_history')
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE, related_name='borrowing_history')
    branch = models.ForeignKey('library_branches.LibraryBranch', on_delete=models.CASCADE, related_name='borrowing_history')
    borrowed_date = models.DateTimeField()
    returned_date = models.DateTimeField(blank=True, null=True)
    days_borrowed = models.PositiveIntegerField(blank=True, null=True)
    was_overdue = models.BooleanField(default=False)
    fine_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    renewal_count = models.PositiveIntegerField(default=0)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='borrowed')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Borrowing History'
        verbose_name_plural = 'Borrowing Histories'
        ordering = ['-borrowed_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.action})"
