from django.contrib import admin
from django.utils.html import format_html
from .models import Author, Publisher, Category, Book, BookCopy, BookReservation

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'nationality', 'birth_date', 'death_date')
    list_filter = ('nationality', 'birth_date')
    search_fields = ('first_name', 'last_name', 'biography')
    date_hierarchy = 'birth_date'

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'established_year', 'contact_email', 'website')
    list_filter = ('established_year',)
    search_fields = ('name', 'address', 'contact_email')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category', 'description')
    list_filter = ('parent_category',)
    search_fields = ('name', 'description')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_list', 'publisher', 'publication_date', 
                   'language', 'format', 'is_active', 'total_copies_count', 'available_copies_count')
    list_filter = ('language', 'format', 'is_active', 'publication_date', 'category', 'publisher')
    search_fields = ('title', 'subtitle', 'isbn', 'description')
    filter_horizontal = ('authors',)
    date_hierarchy = 'publication_date'
    readonly_fields = ('created_at', 'updated_at', 'total_copies_count', 'available_copies_count')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'isbn', 'authors', 'publisher')
        }),
        ('Publication Details', {
            'fields': ('publication_date', 'edition', 'pages', 'language', 'format', 'category')
        }),
        ('Content', {
            'fields': ('description', 'cover_image')
        }),
        ('Financial', {
            'fields': ('price',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'total_copies_count', 'available_copies_count'),
            'classes': ('collapse',)
        }),
    )

@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('book', 'branch', 'copy_number', 'barcode', 'status', 'condition')
    list_filter = ('status', 'condition', 'branch', 'acquisition_date')
    search_fields = ('book__title', 'barcode', 'copy_number')
    raw_id_fields = ('book',)
    date_hierarchy = 'acquisition_date'

@admin.register(BookReservation)
class BookReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'branch', 'reservation_type', 'status', 
                   'reserved_at', 'expires_at')
    list_filter = ('reservation_type', 'status', 'branch', 'reserved_at')
    search_fields = ('user__username', 'book__title')
    raw_id_fields = ('user', 'book')
    date_hierarchy = 'reserved_at'
    readonly_fields = ('reserved_at',)
