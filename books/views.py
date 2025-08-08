from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum
from django.db import models
from .models import Book, BookCopy, BookReservation, Author, Publisher, Category
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum
from .models import Book, BookCopy, BookReservation, Author, Publisher, Category

class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Book.objects.filter(is_active=True).prefetch_related('authors')
        
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

class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        context['available_copies'] = book.book_copies.filter(status='available')
        context['user_can_reserve'] = (
            self.request.user.is_authenticated and 
            not book.reservations.filter(user=self.request.user, status='active').exists()
        )
        return context

class BookSearchView(TemplateView):
    template_name = 'books/search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['authors'] = Author.objects.all()
        return context

class BookByCategoryView(ListView):
    model = Book
    template_name = 'books/by_category.html'
    context_object_name = 'books'
    paginate_by = 12
    
    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return Book.objects.filter(category_id=category_id, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, id=self.kwargs.get('category_id'))
        return context

class BookByAuthorView(ListView):
    model = Book
    template_name = 'books/by_author.html'
    context_object_name = 'books'
    paginate_by = 12
    
    def get_queryset(self):
        author_id = self.kwargs.get('author_id')
        return Book.objects.filter(authors__id=author_id, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = get_object_or_404(Author, id=self.kwargs.get('author_id'))
        return context

# Librarian views
class LibrarianRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_librarian

class BookManageListView(LibrarianRequiredMixin, ListView):
    model = Book
    template_name = 'books/manage_list.html'
    context_object_name = 'books'
    paginate_by = 20

class BookCreateView(LibrarianRequiredMixin, CreateView):
    model = Book
    template_name = 'books/create.html'
    fields = ['title', 'subtitle', 'isbn', 'authors', 'publisher', 'publication_date',
              'edition', 'pages', 'language', 'format', 'category', 'description', 
              'cover_image', 'price']
    success_url = reverse_lazy('books:manage_list')

class BookEditView(LibrarianRequiredMixin, UpdateView):
    model = Book
    template_name = 'books/edit.html'
    fields = ['title', 'subtitle', 'isbn', 'authors', 'publisher', 'publication_date',
              'edition', 'pages', 'language', 'format', 'category', 'description', 
              'cover_image', 'price', 'is_active']
    
    def get_success_url(self):
        return reverse_lazy('books:book_detail', kwargs={'pk': self.object.pk})

class BookDeleteView(LibrarianRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/delete.html'
    success_url = reverse_lazy('books:manage_list')

class BookCopyListView(LibrarianRequiredMixin, ListView):
    model = BookCopy
    template_name = 'books/copy_list.html'
    context_object_name = 'object_list'
    paginate_by = 12
    
    def get_queryset(self):
        book_id = self.kwargs.get('book_id')
        queryset = BookCopy.objects.filter(book_id=book_id).select_related('branch')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(barcode__icontains=search) |
                Q(copy_number__icontains=search) |
                Q(section__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by condition
        condition = self.request.GET.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
            
        return queryset.order_by('copy_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book_id = self.kwargs.get('book_id')
        book = get_object_or_404(Book, id=book_id)
        context['book'] = book
        
        # Add statistics
        all_copies = BookCopy.objects.filter(book=book)
        context['total_copies'] = all_copies.count()
        context['available_copies'] = all_copies.filter(status='available').count()
        context['borrowed_copies'] = all_copies.filter(status='borrowed').count()
        context['reserved_copies'] = all_copies.filter(status='reserved').count()
        
        return context

class BookCopyCreateView(LibrarianRequiredMixin, CreateView):
    model = BookCopy
    template_name = 'books/copy_create.html'
    fields = ['book', 'branch', 'section', 'copy_number', 'barcode', 
              'status', 'condition', 'acquisition_date', 'notes']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from library_branches.models import LibraryBranch
        
        context['books'] = Book.objects.filter(is_active=True).order_by('title')
        context['branches'] = LibraryBranch.objects.filter(is_active=True).order_by('name')
        
        # Pre-select book if provided in query parameters
        book_id = self.request.GET.get('book')
        if book_id:
            try:
                book = Book.objects.get(id=book_id)
                context['form'].fields['book'].initial = book
            except Book.DoesNotExist:
                pass
                
        return context
    
    def get_success_url(self):
        # Redirect to the copy list for the book if available
        if self.object.book:
            return reverse_lazy('books:copy_list', kwargs={'book_id': self.object.book.id})
        return reverse_lazy('books:manage_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Book copy "{form.instance.copy_number}" has been added successfully!')
        return super().form_valid(form)

class BookCopyEditView(LibrarianRequiredMixin, UpdateView):
    model = BookCopy
    template_name = 'books/copy_edit.html'
    fields = ['branch', 'section', 'copy_number', 'barcode', 'status', 
              'condition', 'last_maintenance_date', 'notes']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from library_branches.models import LibraryBranch
        
        context['branches'] = LibraryBranch.objects.filter(is_active=True).order_by('name')
        return context
    
    def get_success_url(self):
        return reverse_lazy('books:copy_list', kwargs={'book_id': self.object.book.id})
    
    def form_valid(self, form):
        messages.success(self.request, f'Book copy "{form.instance.copy_number}" has been updated successfully!')
        return super().form_valid(form)

class BookReserveView(LoginRequiredMixin, TemplateView):
    template_name = 'books/reserve.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = get_object_or_404(Book, id=self.kwargs.get('pk'))
        return context
    
    def post(self, request, *args, **kwargs):
        book = get_object_or_404(Book, id=self.kwargs.get('pk'))
        
        # Check if user already has an active reservation for this book
        existing_reservation = BookReservation.objects.filter(
            user=request.user, 
            book=book, 
            status='active'
        ).first()
        
        if existing_reservation:
            messages.error(request, 'You already have an active reservation for this book.')
            return redirect('books:book_detail', pk=book.id)
        
        # Check if there are available copies
        available_copies = book.book_copies.filter(status='available').count()
        if available_copies == 0:
            messages.error(request, 'No copies available for reservation.')
            return redirect('books:book_detail', pk=book.id)
        
        # Create the reservation
        from library_branches.models import LibraryBranch
        from django.utils import timezone
        from datetime import timedelta
        
        # Get the first available branch (since you don't need more than 1 branch)
        branch = LibraryBranch.objects.first()
        if not branch:
            messages.error(request, 'No library branch available.')
            return redirect('books:book_detail', pk=book.id)
        
        reservation = BookReservation.objects.create(
            user=request.user,
            book=book,
            branch=branch,
            reservation_type='regular',
            status='active',
            expires_at=timezone.now() + timedelta(days=7)  # 7 days to pick up
        )
        
        messages.success(request, f'Book "{book.title}" has been reserved successfully!')
        return redirect('books:reservation_list')

class ReservationListView(LoginRequiredMixin, ListView):
    model = BookReservation
    template_name = 'books/reservation_list.html'
    context_object_name = 'reservations'
    
    def get_queryset(self):
        return BookReservation.objects.filter(user=self.request.user)

class ReservationCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            reservation = get_object_or_404(BookReservation, pk=pk, user=request.user)
            if reservation.status == 'active':
                reservation.status = 'cancelled'
                reservation.save()
                messages.success(request, f'Reservation for "{reservation.book.title}" has been cancelled.')
            else:
                messages.error(request, 'This reservation cannot be cancelled.')
        except BookReservation.DoesNotExist:
            messages.error(request, 'Reservation not found.')
        
        return redirect('books:reservation_list')

class AuthorListView(ListView):
    model = Author
    template_name = 'books/author_list.html'
    context_object_name = 'authors'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Author.objects.all()
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(nationality__icontains=search) |
                Q(biography__icontains=search)
            ).distinct()
        
        return queryset.order_by('last_name', 'first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_books'] = Book.objects.count()
        context['authors_with_books'] = Author.objects.filter(books__isnull=False).distinct().count()
        return context

class AuthorDetailView(DetailView):
    model = Author
    template_name = 'books/author_detail.html'
    context_object_name = 'author'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = self.get_object().books.filter(is_active=True)
        return context

class PublisherListView(ListView):
    model = Publisher
    template_name = 'books/publisher_list.html'
    context_object_name = 'publishers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Publisher.objects.all()
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(contact_email__icontains=search) |
                Q(website__icontains=search) |
                Q(address__icontains=search)
            ).distinct()
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_books'] = Book.objects.count()
        context['publishers_with_books'] = Publisher.objects.filter(books__isnull=False).distinct().count()
        return context
    paginate_by = 20

class CategoryListView(ListView):
    model = Category
    template_name = 'books/category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'books/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = self.get_object().book_set.filter(is_active=True)
        return context

class LibrarianDashboardView(LibrarianRequiredMixin, TemplateView):
    template_name = 'books/librarian_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models import User
        from borrowing.models import BorrowTransaction
        from fines.models import Fine
        from django.utils import timezone
        from datetime import timedelta
        
        # Book statistics
        context['total_books'] = Book.objects.count()
        context['active_books'] = Book.objects.filter(is_active=True).count()
        context['total_copies'] = BookCopy.objects.count()
        context['available_copies'] = BookCopy.objects.filter(status='available').count()
        
        # Member statistics
        context['total_members'] = User.objects.filter(user_type='member').count()
        context['active_members'] = User.objects.filter(user_type='member', is_active_member=True).count()
        
        # Borrowing statistics
        context['active_borrowings'] = BorrowTransaction.objects.filter(status='active').count()
        context['overdue_books'] = BorrowTransaction.objects.filter(
            status='active',
            due_date__lt=timezone.now().date()
        ).count()
        
        # Fine statistics
        context['unpaid_fines'] = Fine.objects.filter(status='unpaid').count()
        context['total_fine_amount'] = Fine.objects.filter(status='unpaid').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Recent activities
        context['recent_borrowings'] = BorrowTransaction.objects.filter(
            status='active'
        ).order_by('-borrowed_at')[:5].select_related('user', 'book_copy__book')
        
        context['recent_returns'] = BorrowTransaction.objects.filter(
            status='returned'
        ).order_by('-returned_at')[:5].select_related('user', 'book_copy__book')
        
        # Books due soon
        due_soon_date = timezone.now().date() + timedelta(days=3)
        context['books_due_soon'] = BorrowTransaction.objects.filter(
            status='active',
            due_date__lte=due_soon_date,
            due_date__gte=timezone.now().date()
        ).order_by('due_date')[:10].select_related('user', 'book_copy__book')
        
        return context

# Author Management Views
class AuthorCreateView(LibrarianRequiredMixin, CreateView):
    model = Author
    template_name = 'books/author_create.html'
    fields = ['first_name', 'last_name', 'biography', 'birth_date', 'death_date', 'nationality']
    success_url = reverse_lazy('books:author_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Author "{form.instance.full_name}" has been added successfully!')
        return super().form_valid(form)

class AuthorEditView(LibrarianRequiredMixin, UpdateView):
    model = Author
    template_name = 'books/author_edit.html'
    fields = ['first_name', 'last_name', 'biography', 'birth_date', 'death_date', 'nationality']
    
    def get_success_url(self):
        return reverse_lazy('books:author_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f'Author "{form.instance.full_name}" has been updated successfully!')
        return super().form_valid(form)

class AuthorDeleteView(LibrarianRequiredMixin, DeleteView):
    model = Author
    template_name = 'books/author_delete.html'
    success_url = reverse_lazy('books:author_list')

# Publisher Management Views
class PublisherCreateView(LibrarianRequiredMixin, CreateView):
    model = Publisher
    template_name = 'books/publisher_create.html'
    fields = ['name', 'address', 'website', 'contact_email', 'established_year']
    success_url = reverse_lazy('books:publisher_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Publisher "{form.instance.name}" has been added successfully!')
        return super().form_valid(form)

class PublisherEditView(LibrarianRequiredMixin, UpdateView):
    model = Publisher
    template_name = 'books/publisher_edit.html'
    fields = ['name', 'address', 'website', 'contact_email', 'established_year']
    success_url = reverse_lazy('books:publisher_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Publisher "{form.instance.name}" has been updated successfully!')
        return super().form_valid(form)

class PublisherDeleteView(LibrarianRequiredMixin, DeleteView):
    model = Publisher
    template_name = 'books/publisher_delete.html'
    success_url = reverse_lazy('books:publisher_list')

# Category Management Views  
class CategoryCreateView(LibrarianRequiredMixin, CreateView):
    model = Category
    template_name = 'books/category_create.html'
    fields = ['name', 'description', 'parent_category']
    success_url = reverse_lazy('books:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" has been added successfully!')
        return super().form_valid(form)

class CategoryEditView(LibrarianRequiredMixin, UpdateView):
    model = Category
    template_name = 'books/category_edit.html'
    fields = ['name', 'description', 'parent_category']
    success_url = reverse_lazy('books:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" has been updated successfully!')
        return super().form_valid(form)

class CategoryDeleteView(LibrarianRequiredMixin, DeleteView):
    model = Category
    template_name = 'books/category_delete.html'
    success_url = reverse_lazy('books:category_list')
