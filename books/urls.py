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
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    path('publishers/', views.PublisherListView.as_view(), name='publisher_list'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
]