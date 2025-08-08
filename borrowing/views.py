from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
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
            status='available'
        ).count()
        
        # Recent borrowings (last 5)
        context['recent_borrowings'] = current_borrowings.order_by('-borrowed_at')[:5]
        
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book_copy_id = self.request.GET.get('book_copy_id')
        if book_copy_id:
            from books.models import BookCopy
            try:
                book_copy = BookCopy.objects.get(id=book_copy_id, status='available')
                context['book_copy'] = book_copy
            except BookCopy.DoesNotExist:
                context['error'] = 'Book copy not found or not available.'
        else:
            # Show available books for borrowing
            from books.models import BookCopy
            context['available_copies'] = BookCopy.objects.filter(
                status='available', 
                book__is_active=True
            ).select_related('book').prefetch_related('book__authors')[:20]
        return context
    
    def post(self, request, *args, **kwargs):
        book_copy_id = request.POST.get('book_copy_id')
        if not book_copy_id:
            messages.error(request, 'No book copy selected for borrowing.')
            return redirect('borrowing:borrow')
        
        from books.models import BookCopy
        from django.utils import timezone
        from datetime import timedelta
        
        try:
            book_copy = BookCopy.objects.get(id=book_copy_id, status='available')
        except BookCopy.DoesNotExist:
            messages.error(request, 'Book copy not found or not available.')
            return redirect('borrowing:borrow')
        
        # Check if user already has this book borrowed
        existing_transaction = BorrowTransaction.objects.filter(
            user=request.user,
            book_copy__book=book_copy.book,
            status='active'
        ).first()
        
        if existing_transaction:
            messages.error(request, 'You already have this book borrowed.')
            return redirect('borrowing:current')
        
        # Create the borrow transaction
        due_date = timezone.now() + timedelta(days=14)  # 2 weeks loan period
        
        transaction = BorrowTransaction.objects.create(
            user=request.user,
            book_copy=book_copy,
            due_date=due_date,
            status='active'
        )
        
        # Update book copy status
        book_copy.status = 'borrowed'
        book_copy.save()
        
        messages.success(request, f'Book "{book_copy.book.title}" has been borrowed successfully!')
        return redirect('borrowing:current')

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
