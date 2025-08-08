from django.urls import path
from . import views

app_name = 'borrowing'

urlpatterns = [
    # Dashboard and overview
    path('', views.BorrowingDashboardView.as_view(), name='dashboard'),
    path('combined-dashboard/', views.CombinedDashboardView.as_view(), name='combined_dashboard'),
    
    # Current borrowings
    path('current/', views.CurrentBorrowingsView.as_view(), name='current'),
    path('history/', views.BorrowingHistoryView.as_view(), name='history'),
    
    # Borrowing actions
    path('borrow/', views.BorrowBookView.as_view(), name='borrow'),
    path('borrow/<int:book_copy_id>/', views.BorrowConfirmationView.as_view(), name='borrow_confirmation'),
    path('return/', views.ReturnBookView.as_view(), name='return'),
    path('return/<int:transaction_id>/', views.ReturnConfirmationView.as_view(), name='return_confirmation'),
    path('renew/<int:transaction_id>/', views.RenewBookView.as_view(), name='renew'),
    
    # Book browsing for borrowing
    path('browse/', views.BrowseBooksView.as_view(), name='browse_books'),
    
    # Librarian functions
    path('manage/', views.BorrowingManageView.as_view(), name='manage'),
    path('overdue/', views.OverdueBooksView.as_view(), name='overdue'),
    path('process-return/<int:transaction_id>/', views.ProcessReturnView.as_view(), name='process_return'),
    path('issue-book/', views.IssueBookView.as_view(), name='issue_book'),
]
