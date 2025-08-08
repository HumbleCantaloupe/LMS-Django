from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from .models import BorrowTransaction, BorrowingHistory
from books.models import Book, BookCopy

class BorrowingDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Current borrowings
        current_borrowings = BorrowTransaction.objects.filter(
            user=user, status='active'
        ).select_related('book_copy__book')
        
        # Statistics
        context['current_borrowings_count'] = current_borrowings.count()
        
        # Overdue books
        today = timezone.now().date()
        overdue_transactions = current_borrowings.filter(due_date__lt=today)
        context['overdue_count'] = overdue_transactions.count()
        
        # Total borrowed (all time)
        context['total_borrowed'] = BorrowingHistory.objects.filter(user=user).count()
        
        # Available books
        context['available_books'] = BookCopy.objects.filter(
            is_active=True, status='available'
        ).count()
        
        # Recent borrowings (last 5)
        context['recent_borrowings'] = current_borrowings.order_by('-borrow_date')[:5]
        
        # Due soon (within 3 days)
        due_soon_date = today + timedelta(days=3)
        context['due_soon'] = current_borrowings.filter(
            due_date__lte=due_soon_date,
            due_date__gte=today
        ).order_by('due_date')[:5]
        
        return context

class CurrentBorrowingsView(LoginRequiredMixin, ListView):
    model = BorrowTransaction
    template_name = 'borrowing/current.html'
    context_object_name = 'transactions'
    paginate_by = 9
    
    def get_queryset(self):
        return BorrowTransaction.objects.filter(
            user=self.request.user, status='active'
        ).select_related('book_copy__book').prefetch_related('book_copy__book__authors')

class BorrowingHistoryView(LoginRequiredMixin, ListView):
    model = BorrowingHistory
    template_name = 'borrowing/history.html'
    context_object_name = 'history'
    paginate_by = 20
    
    def get_queryset(self):
        return BorrowingHistory.objects.filter(
            user=self.request.user
        ).select_related('book_copy__book').prefetch_related('book_copy__book__authors')

class ReturnBookView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/return.html'

class RenewBookView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/renew.html'

class BorrowBookView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/borrow.html'

class CombinedDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/combined_dashboard.html'

class BrowseBooksView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'borrowing/browse_books.html'
    context_object_name = 'books'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Book.objects.filter(is_active=True).prefetch_related('authors', 'book_copies')
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(authors__first_name__icontains=search) |
                Q(authors__last_name__icontains=search) |
                Q(isbn__icontains=search)
            ).distinct()
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
            
        return queryset.order_by('title')

class BorrowConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/borrow_confirmation.html'

class ReturnConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/return_confirmation.html'

class BorrowingManageView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/manage.html'

class OverdueBooksView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/overdue.html'

class ProcessReturnView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/process_return.html'

class IssueBookView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/issue_book.html'
