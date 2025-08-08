from django.contrib import admin
from .models import BorrowTransaction, BorrowingHistory, ReturnTransaction

@admin.register(BorrowTransaction)
class BorrowTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'book_copy', 'borrowed_at', 'due_date', 'status', 'is_overdue', 'renewal_count')
    list_filter = ('status', 'borrowed_at', 'due_date')
    search_fields = ('user__username', 'book_copy__book__title', 'book_copy__barcode')
    raw_id_fields = ('user', 'book_copy', 'librarian_issued', 'librarian_returned')
    date_hierarchy = 'borrowed_at'
    readonly_fields = ('borrowed_at', 'is_overdue', 'days_overdue', 'fine_amount')

@admin.register(BorrowingHistory)
class BorrowingHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrowed_date', 'returned_date', 'fine_paid', 'action')
    list_filter = ('action', 'borrowed_date', 'returned_date', 'was_overdue')
    search_fields = ('user__username', 'book__title')
    raw_id_fields = ('user', 'book', 'branch')
    date_hierarchy = 'borrowed_date'
    readonly_fields = ('borrowed_date', 'created_at')

@admin.register(ReturnTransaction)
class ReturnTransactionAdmin(admin.ModelAdmin):
    list_display = ('borrow_transaction', 'librarian', 'returned_at', 'condition', 'total_penalty')
    list_filter = ('condition', 'returned_at')
    search_fields = ('borrow_transaction__user__username', 'borrow_transaction__book_copy__book__title')
    raw_id_fields = ('borrow_transaction', 'librarian')
    readonly_fields = ('returned_at', 'total_penalty')
