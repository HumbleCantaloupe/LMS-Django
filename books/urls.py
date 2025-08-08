from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # Book browsing
    path('', views.BookListView.as_view(), name='book_list'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('search/', views.BookSearchView.as_view(), name='search'),
    path('category/<int:category_id>/', views.BookByCategoryView.as_view(), name='by_category'),
    path('author/<int:author_id>/', views.BookByAuthorView.as_view(), name='by_author'),
    
    # Book management (for librarians)
    path('librarian/', views.LibrarianDashboardView.as_view(), name='librarian_dashboard'),
    path('manage/', views.BookManageListView.as_view(), name='manage_list'),
    path('create/', views.BookCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.BookEditView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.BookDeleteView.as_view(), name='delete'),
    
    # Book copies
    path('<int:book_id>/copies/', views.BookCopyListView.as_view(), name='copy_list'),
    path('copies/create/', views.BookCopyCreateView.as_view(), name='copy_create'),
    path('copies/<int:pk>/edit/', views.BookCopyEditView.as_view(), name='copy_edit'),
    
    # Reservations
    path('<int:pk>/reserve/', views.BookReserveView.as_view(), name='reserve'),
    path('reservations/', views.ReservationListView.as_view(), name='reservation_list'),
    path('reservations/<int:pk>/cancel/', views.ReservationCancelView.as_view(), name='reservation_cancel'),
    
    # Authors and Publishers
    path('authors/', views.AuthorListView.as_view(), name='author_list'),
    path('authors/create/', views.AuthorCreateView.as_view(), name='author_create'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    path('authors/<int:pk>/edit/', views.AuthorEditView.as_view(), name='author_edit'),
    path('authors/<int:pk>/delete/', views.AuthorDeleteView.as_view(), name='author_delete'),
    
    path('publishers/', views.PublisherListView.as_view(), name='publisher_list'),
    path('publishers/create/', views.PublisherCreateView.as_view(), name='publisher_create'),
    path('publishers/<int:pk>/edit/', views.PublisherEditView.as_view(), name='publisher_edit'),
    path('publishers/<int:pk>/delete/', views.PublisherDeleteView.as_view(), name='publisher_delete'),
    
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/<int:pk>/edit/', views.CategoryEditView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Librarian Dashboard
    path('dashboard/', views.LibrarianDashboardView.as_view(), name='dashboard'),
]