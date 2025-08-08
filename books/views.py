from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from django.urls import reverse_lazy
from django.db.models import Q, Count
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
        return reverse_lazy('books:detail', kwargs={'pk': self.object.pk})

class BookDeleteView(LibrarianRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/delete.html'
    success_url = reverse_lazy('books:manage_list')

class BookCopyListView(LibrarianRequiredMixin, ListView):
    model = BookCopy
    template_name = 'books/copy_list.html'
    context_object_name = 'copies'
    
    def get_queryset(self):
        book_id = self.kwargs.get('book_id')
        return BookCopy.objects.filter(book_id=book_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = get_object_or_404(Book, id=self.kwargs.get('book_id'))
        return context

class BookCopyCreateView(LibrarianRequiredMixin, CreateView):
    model = BookCopy
    template_name = 'books/copy_create.html'
    fields = ['book', 'branch', 'section', 'copy_number', 'barcode', 
              'condition', 'acquisition_date']
    success_url = reverse_lazy('books:manage_list')

class BookCopyEditView(LibrarianRequiredMixin, UpdateView):
    model = BookCopy
    template_name = 'books/copy_edit.html'
    fields = ['branch', 'section', 'copy_number', 'barcode', 'status', 
              'condition', 'last_maintenance_date', 'notes']
    
    def get_success_url(self):
        return reverse_lazy('books:copy_list', kwargs={'book_id': self.object.book.id})

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

class CategoryListView(ListView):
    model = Category
    template_name = 'books/category_list.html'
    context_object_name = 'categories'
