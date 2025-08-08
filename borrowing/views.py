from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import BorrowTransaction, BorrowingHistory
from books.models import Book, BookCopy

class BorrowingDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        current_borrowings = BorrowTransaction.objects.filter(
            user=user, status='active'
        ).select_related('book_copy__book')
        
        context['current_borrowings_count'] = current_borrowings.count()
        
        today = timezone.now().date()
        overdue_transactions = current_borrowings.filter(due_date__lt=today)
        context['overdue_count'] = overdue_transactions.count()
        
        context['total_borrowed'] = BorrowingHistory.objects.filter(user=user).count()
        
        context['available_books'] = BookCopy.objects.filter(
            status='available'
        ).count()
        
        context['recent_borrowings'] = current_borrowings.order_by('-borrowed_at')[:5]
        
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_transactions'] = BorrowTransaction.objects.filter(
            user=self.request.user,
            status='active'
        ).select_related('book_copy__book').prefetch_related('book_copy__book__authors')
        return context

class RenewBookView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/renew.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction_id = kwargs.get('transaction_id')
        
        try:
            transaction = BorrowTransaction.objects.get(
                id=transaction_id,
                user=self.request.user,
                status='active'
            )
            context['transaction'] = transaction
            
            can_renew = True
            renewal_error = None
            
            if transaction.renewal_count >= transaction.max_renewals_allowed:
                can_renew = False
                renewal_error = f"This book has already been renewed the maximum number of times ({transaction.max_renewals_allowed})."
            
            from books.models import BookReservation
            if BookReservation.objects.filter(
                book=transaction.book_copy.book,
                status='active'
            ).exclude(user=self.request.user).exists():
                can_renew = False
                renewal_error = "This book is reserved by another user and cannot be renewed."
            
            from fines.models import Fine
            if Fine.objects.filter(
                user=self.request.user,
                status='unpaid'
            ).exists():
                can_renew = False
                renewal_error = "You have unpaid fines. Please pay all fines before renewing books."
            
            context['can_renew'] = can_renew
            context['renewal_error'] = renewal_error
            
            from datetime import timedelta
            new_due_date = timezone.now() + timedelta(days=14)
            context['new_due_date'] = new_due_date.date()
            
        except BorrowTransaction.DoesNotExist:
            context['error'] = 'Transaction not found or you do not have permission to renew this book.'
        
        return context
    
    def post(self, request, *args, **kwargs):
        transaction_id = kwargs.get('transaction_id')
        
        try:
            transaction = BorrowTransaction.objects.get(
                id=transaction_id,
                user=request.user,
                status='active'
            )
            
            can_renew = True
            renewal_error = None
            
            if transaction.renewal_count >= transaction.max_renewals_allowed:
                can_renew = False
                renewal_error = f"This book has already been renewed the maximum number of times ({transaction.max_renewals_allowed})."
            
            from books.models import BookReservation
            if BookReservation.objects.filter(
                book=transaction.book_copy.book,
                status='active'
            ).exclude(user=request.user).exists():
                can_renew = False
                renewal_error = "This book is reserved by another user and cannot be renewed."
            
            from fines.models import Fine
            if Fine.objects.filter(
                user=request.user,
                status='unpaid'
            ).exists():
                can_renew = False
                renewal_error = "You have unpaid fines. Please pay all fines before renewing books."
            
            if not can_renew:
                messages.error(request, renewal_error or 'This book cannot be renewed at this time.')
                return redirect('borrowing:renew', transaction_id=transaction_id)
            
            from datetime import timedelta
            new_due_date = timezone.now() + timedelta(days=14)
            transaction.due_date = new_due_date
            
            transaction.renewal_count += 1
            
            transaction.save()
            
            messages.success(request, f'Book "{transaction.book_copy.book.title}" has been renewed successfully. New due date: {new_due_date.strftime("%B %d, %Y")}')
            return redirect('borrowing:current')
            
        except BorrowTransaction.DoesNotExist:
            messages.error(request, 'Transaction not found or you do not have permission to renew this book.')
            return redirect('borrowing:current')

class BorrowBookView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/borrow.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book_copy_id = self.request.GET.get('book_copy_id')
        book_id = self.request.GET.get('book')
        
        if book_copy_id:
            from books.models import BookCopy
            try:
                book_copy = BookCopy.objects.get(id=book_copy_id, status='available')
                context['book_copy'] = book_copy
                context['book'] = book_copy.book
            except BookCopy.DoesNotExist:
                context['error'] = 'Book copy not found or not available.'
        elif book_id:
            from books.models import Book, BookCopy
            try:
                book = Book.objects.get(id=book_id, is_active=True)
                available_copies = BookCopy.objects.filter(
                    book=book, 
                    status='available'
                ).select_related('branch', 'section')
                
                context['book'] = book
                context['available_copies'] = available_copies
                
                if not available_copies.exists():
                    context['error'] = 'No copies of this book are currently available for borrowing.'
            except Book.DoesNotExist:
                context['error'] = 'Book not found.'
        else:
            from books.models import BookCopy
            context['available_copies'] = BookCopy.objects.filter(
                status='available', 
                book__is_active=True
            ).select_related('book', 'branch').prefetch_related('book__authors')[:20]
            context['show_all_books'] = True
        return context
    
    def post(self, request, *args, **kwargs):
        book_copy_id = request.POST.get('book_copy_id')
        book_id = request.POST.get('book_id')
        
        if not book_copy_id and not book_id:
            messages.error(request, 'No book or book copy selected for borrowing.')
            return redirect('borrowing:borrow')
        
        from books.models import BookCopy, Book
        from django.utils import timezone
        from datetime import timedelta
        
        if book_id and not book_copy_id:
            try:
                book = Book.objects.get(id=book_id, is_active=True)
                available_copy = BookCopy.objects.filter(
                    book=book, 
                    status='available'
                ).first()
                
                if not available_copy:
                    messages.error(request, f'No copies of "{book.title}" are currently available.')
                    return redirect('borrowing:borrow')
                
                book_copy = available_copy
            except Book.DoesNotExist:
                messages.error(request, 'Book not found.')
                return redirect('borrowing:borrow')
        else:
            try:
                book_copy = BookCopy.objects.get(id=book_copy_id, status='available')
            except BookCopy.DoesNotExist:
                messages.error(request, 'Book copy not found or not available.')
                return redirect('borrowing:borrow')
        
        existing_transaction = BorrowTransaction.objects.filter(
            user=request.user,
            book_copy__book=book_copy.book,
            status='active'
        ).first()
        
        if existing_transaction:
            messages.error(request, 'You already have this book borrowed.')
            return redirect('borrowing:current')
        
        due_date = timezone.now() + timedelta(days=14)
        
        transaction = BorrowTransaction.objects.create(
            user=request.user,
            book_copy=book_copy,
            due_date=due_date,
            status='active'
        )
        
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

class ReturnConfirmationView(LoginRequiredMixin, View):
    template_name = 'borrowing/return_confirmation.html'
    
    def get(self, request, transaction_id):
        try:
            transaction = BorrowTransaction.objects.get(
                id=transaction_id,
                user=request.user,
                status='active'
            )
        except BorrowTransaction.DoesNotExist:
            messages.error(request, 'Transaction not found or already returned.')
            return redirect('borrowing:current')
        
        context = {
            'transaction': transaction,
            'book': transaction.book_copy.book,
            'is_overdue': transaction.is_overdue,
            'days_overdue': transaction.days_overdue,
            'fine_amount': transaction.fine_amount,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, transaction_id):
        from django.utils import timezone
        from fines.models import Fine
        
        try:
            transaction = BorrowTransaction.objects.get(
                id=transaction_id,
                user=request.user,
                status='active'
            )
        except BorrowTransaction.DoesNotExist:
            messages.error(request, 'Transaction not found or already returned.')
            return redirect('borrowing:current')
        
        fine_amount = Decimal('0.00')
        if transaction.is_overdue:
            fine_amount = transaction.fine_amount
        
        transaction.status = 'returned'
        transaction.returned_at = timezone.now()
        transaction.save()
        
        book_copy = transaction.book_copy
        book_copy.status = 'available'
        book_copy.save()
        
        if fine_amount > 0:
            Fine.objects.create(
                user=request.user,
                borrow_transaction=transaction,
                amount=fine_amount,
                reason='overdue',
                description=f'Late return fine for "{transaction.book_copy.book.title}" - {transaction.days_overdue} days overdue'
            )
            messages.warning(
                request, 
                f'Book returned successfully! A fine of MVR {fine_amount} has been added to your account for late return.'
            )
        else:
            messages.success(request, f'Book "{transaction.book_copy.book.title}" returned successfully!')
        
        from .models import BorrowingHistory
        BorrowingHistory.objects.create(
            user=request.user,
            book=transaction.book_copy.book,
            branch=transaction.book_copy.branch,
            borrowed_date=transaction.borrowed_at,
            returned_date=timezone.now(),
            action='returned'
        )
        
        return redirect('borrowing:current')

class BorrowingManageView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/manage.html'

class OverdueBooksView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/overdue.html'

class ProcessReturnView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/process_return.html'

class IssueBookView(LoginRequiredMixin, TemplateView):
    template_name = 'borrowing/issue_book.html'
