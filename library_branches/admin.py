from django.contrib import admin
from .models import LibraryBranch, LibrarySection, BranchOperatingHours

class BranchOperatingHoursInline(admin.TabularInline):
    model = BranchOperatingHours
    extra = 0

@admin.register(LibraryBranch)
class LibraryBranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'manager_name', 'is_active', 'current_book_count', 'capacity_percentage')
    list_filter = ('is_active', 'established_date', 'wifi_available', 'parking_available')
    search_fields = ('name', 'code', 'address', 'manager_name')
    readonly_fields = ('created_at', 'updated_at', 'current_book_count', 'available_books_count', 'capacity_percentage')
    date_hierarchy = 'established_date'
    inlines = [BranchOperatingHoursInline]

@admin.register(LibrarySection)
class LibrarySectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'section_type', 'floor_number', 'current_book_count', 'capacity_percentage')
    list_filter = ('section_type', 'floor_number', 'is_restricted', 'branch')
    search_fields = ('name', 'description', 'branch__name')
    readonly_fields = ('created_at', 'updated_at', 'current_book_count', 'capacity_percentage')

@admin.register(BranchOperatingHours)
class BranchOperatingHoursAdmin(admin.ModelAdmin):
    list_display = ('branch', 'weekday', 'opening_time', 'closing_time', 'is_closed')
    list_filter = ('weekday', 'is_closed', 'branch')
    search_fields = ('branch__name',)
