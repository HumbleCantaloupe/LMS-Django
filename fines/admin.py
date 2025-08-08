from django.contrib import admin
from .models import FineType, Fine, FinePayment

@admin.register(FineType)
class FineTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_amount', 'is_per_day', 'is_active')
    list_filter = ('is_per_day', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('user', 'fine_type', 'amount', 'amount_paid', 'status', 'issued_date', 'due_date')
    list_filter = ('status', 'fine_type', 'issued_date', 'due_date')
    search_fields = ('user__username', 'description')
    raw_id_fields = ('user', 'borrow_transaction', 'issued_by')
    date_hierarchy = 'issued_date'
    readonly_fields = ('issued_date', 'amount_remaining')
    
    actions = ['mark_as_paid', 'waive_fine']
    
    def mark_as_paid(self, request, queryset):
        for fine in queryset:
            fine.amount_paid = fine.amount
            fine.status = 'paid'
            fine.save()
        self.message_user(request, f'{queryset.count()} fines marked as paid.')
    mark_as_paid.short_description = 'Mark selected fines as paid'
    
    def waive_fine(self, request, queryset):
        queryset.update(status='waived')
        self.message_user(request, f'{queryset.count()} fines waived.')
    waive_fine.short_description = 'Waive selected fines'

@admin.register(FinePayment)
class FinePaymentAdmin(admin.ModelAdmin):
    list_display = ('fine', 'amount', 'payment_method', 'payment_date', 'processed_by')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('fine__user__username', 'reference_number')
    raw_id_fields = ('fine', 'processed_by')
    readonly_fields = ('payment_date',)
