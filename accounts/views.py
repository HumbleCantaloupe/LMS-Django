from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.views.generic import (
    View, TemplateView, ListView, DetailView, 
    CreateView, UpdateView, FormView
)
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum
from django.db import models
from .models import User, UserProfile, AuditLog
from .forms import CustomUserCreationForm, UserProfileForm, MemberEditForm
from borrowing.models import BorrowTransaction
from fines.models import Fine

class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        
        # Create UserProfile for the new user
        UserProfile.objects.get_or_create(user=user)
        
        # Log the user in
        login(self.request, user)
        
        # Create audit log
        AuditLog.objects.create(
            user=user,
            action='account_created',
            description=f'Account created for user {user.username}',
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(self.request, 'Account created successfully! Welcome to the library!')
        return redirect('accounts:profile')
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context.update({
            'current_borrowings': BorrowTransaction.objects.filter(
                user=user, status='active'
            ).select_related('book_copy__book'),
            'pending_fines': Fine.objects.filter(
                user=user, status='pending'
            ).select_related('fine_type'),
            'recent_borrowings': BorrowTransaction.objects.filter(
                user=user
            ).order_by('-borrowed_at')[:5].select_related('book_copy__book'),
        })
        return context

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_librarian:
            # Librarian dashboard
            context.update({
                'total_active_loans': BorrowTransaction.objects.filter(status='active').count(),
                'overdue_books': BorrowTransaction.objects.filter(
                    status='active', due_date__lt=timezone.now()
                ).count(),
                'pending_reservations': user.reservations.filter(status='active').count(),
                'pending_fines': Fine.objects.filter(status='pending').count(),
            })
        else:
            # Member dashboard
            context.update({
                'active_borrowings': BorrowTransaction.objects.filter(
                    user=user, status='active'
                ).count(),
                'total_fines': Fine.objects.filter(
                    user=user, status='pending'
                ).aggregate(total=Sum('amount'))['total'] or 0,
                'active_reservations': user.reservations.filter(status='active').count(),
            })
        
        return context

class LibrarianRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_librarian

class MemberListView(LibrarianRequiredMixin, ListView):
    model = User
    template_name = 'accounts/member_list.html'
    context_object_name = 'members'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.filter(user_type='member').annotate(
            active_borrowings=Count('borrow_transactions', 
                                  filter=Q(borrow_transactions__status='active'))
        )
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(library_card_number__icontains=search)
            )
        
        return queryset.order_by('-date_joined')

class MemberDetailView(LibrarianRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/member_detail.html'
    context_object_name = 'member'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = self.get_object()
        
        context.update({
            'current_borrowings': BorrowTransaction.objects.filter(
                user=member, status='active'
            ).select_related('book_copy__book'),
            'borrowing_history': BorrowTransaction.objects.filter(
                user=member
            ).order_by('-borrowed_at')[:10].select_related('book_copy__book'),
            'pending_fines': Fine.objects.filter(
                user=member, status='pending'
            ).select_related('fine_type'),
            'audit_logs': AuditLog.objects.filter(
                user=member
            ).order_by('-timestamp')[:20],
        })
        return context

class MemberEditView(LibrarianRequiredMixin, UpdateView):
    model = User
    form_class = MemberEditForm
    template_name = 'accounts/member_edit.html'
    
    def get_success_url(self):
        return reverse_lazy('accounts:member_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f'Member {self.object.username} updated successfully!')
        return super().form_valid(form)

class MemberCreateView(LibrarianRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/member_create.html'
    success_url = reverse_lazy('accounts:member_list')
    
    def form_valid(self, form):
        form.instance.user_type = 'member'
        messages.success(self.request, 'New member created successfully!')
        return super().form_valid(form)
