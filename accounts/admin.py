from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, AuditLog

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 
                   'library_card_number', 'is_active_member', 'membership_date', 'get_borrowed_books_count')
    list_filter = ('user_type', 'is_active_member', 'is_staff', 'is_active', 'date_joined', 'membership_date')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'library_card_number', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Library Information', {
            'fields': ('user_type', 'library_card_number', 'is_active_member', 
                      'membership_date', 'membership_expiry')
        }),
        ('Personal Information', {
            'fields': ('phone_number', 'date_of_birth', 'address', 
                      'emergency_contact_name', 'emergency_contact_phone', 'profile_picture')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Library Information', {
            'fields': ('user_type', 'is_active_member')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
    )
    
    readonly_fields = ('library_card_number', 'date_joined', 'last_login')
    
    def get_borrowed_books_count(self, obj):
        if hasattr(obj, 'borrowtransaction_set'):
            return obj.borrowtransaction_set.filter(status='active').count()
        return 0
    get_borrowed_books_count.short_description = 'Current Borrowings'
    
    actions = ['activate_membership', 'deactivate_membership', 'make_librarian', 'make_member']
    
    def activate_membership(self, request, queryset):
        queryset.update(is_active_member=True)
        self.message_user(request, f'{queryset.count()} users activated successfully.')
    activate_membership.short_description = 'Activate selected users'
    
    def deactivate_membership(self, request, queryset):
        queryset.update(is_active_member=False)
        self.message_user(request, f'{queryset.count()} users deactivated successfully.')
    deactivate_membership.short_description = 'Deactivate selected users'
    
    def make_librarian(self, request, queryset):
        queryset.update(user_type='librarian')
        self.message_user(request, f'{queryset.count()} users promoted to librarian.')
    make_librarian.short_description = 'Promote to librarian'
    
    def make_member(self, request, queryset):
        queryset.update(user_type='member')
        self.message_user(request, f'{queryset.count()} users set as members.')
    make_member.short_description = 'Set as member'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_branch', 'created_at', 'updated_at')
    list_filter = ('preferred_branch', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio')
    raw_id_fields = ('user', 'preferred_branch')
    filter_horizontal = ('reading_preferences',)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'description')
    readonly_fields = ('user', 'action', 'description', 'ip_address', 'user_agent', 
                      'timestamp', 'additional_data')
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
