from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class FineType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    default_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_per_day = models.BooleanField(default=False, help_text="If true, fine amount multiplies by number of days")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Fine(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('waived', 'Waived'),
        ('partial', 'Partially Paid'),
        ('overdue', 'Overdue'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fines')
    fine_type = models.ForeignKey(FineType, on_delete=models.CASCADE, related_name='fines')
    borrow_transaction = models.ForeignKey(
        'borrowing.BorrowTransaction', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='fines'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    issued_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    description = models.TextField(blank=True)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='issued_fines'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-issued_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.fine_type.name} - ${self.amount}"
    
    @property
    def amount_remaining(self):
        return self.amount - self.amount_paid
    
    @property
    def is_overdue(self):
        return timezone.now() > self.due_date and self.status == 'pending'
    
    @property
    def is_fully_paid(self):
        return self.amount_paid >= self.amount
    
    def save(self, *args, **kwargs):
        # Auto-update status based on payment
        if self.is_fully_paid:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        elif self.is_overdue:
            self.status = 'overdue'
        
        super().save(*args, **kwargs)

class FinePayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Debit/Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('waived', 'Waived'),
    ]
    
    fine = models.ForeignKey(Fine, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='processed_payments'
    )
    transaction_id = models.CharField(max_length=100, blank=True)
    receipt_number = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment ${self.amount} for {self.fine}"
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate receipt number
            last_payment = FinePayment.objects.order_by('id').last()
            if last_payment:
                last_number = int(last_payment.receipt_number.replace('RCP', ''))
                self.receipt_number = f"RCP{last_number + 1:06d}"
            else:
                self.receipt_number = "RCP000001"
        
        super().save(*args, **kwargs)
        
        # Update fine amount paid
        self.fine.amount_paid = self.fine.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        self.fine.save()

class MembershipFee(models.Model):
    FEE_TYPE_CHOICES = [
        ('annual', 'Annual Membership'),
        ('monthly', 'Monthly Membership'),
        ('student', 'Student Membership'),
        ('senior', 'Senior Citizen Membership'),
        ('family', 'Family Membership'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('waived', 'Waived'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membership_fees')
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    issued_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    paid_date = models.DateTimeField(blank=True, null=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='processed_membership_fees'
    )
    payment_method = models.CharField(max_length=20, choices=FinePayment.PAYMENT_METHOD_CHOICES, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-issued_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_fee_type_display()} - ${self.amount}"
    
    @property
    def is_overdue(self):
        return timezone.now() > self.due_date and self.status == 'pending'
    
    @property
    def is_active(self):
        return (self.status == 'paid' and 
                self.valid_from <= timezone.now() <= self.valid_until)

class MembershipRenewal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membership_renewals')
    previous_expiry = models.DateTimeField()
    new_expiry = models.DateTimeField()
    renewal_fee = models.DecimalField(max_digits=10, decimal_places=2)
    renewed_date = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='processed_renewals'
    )
    auto_renewal = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-renewed_date']
    
    def __str__(self):
        return f"{self.user.username} - Renewal to {self.new_expiry.date()}"

class PriorityReservationFee(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='priority_fees')
    reservation = models.OneToOneField(
        'books.BookReservation', 
        on_delete=models.CASCADE, 
        related_name='priority_fee'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5.00'))
    paid_date = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='processed_priority_fees'
    )
    payment_method = models.CharField(max_length=20, choices=FinePayment.PAYMENT_METHOD_CHOICES, default='cash')
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - Priority Fee for {self.reservation.book.title}"
