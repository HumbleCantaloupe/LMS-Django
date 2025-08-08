from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from books.models import Book, BookCopy
from borrowing.models import BorrowTransaction
from accounts.models import User

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get dashboard statistics
        context.update({
            'total_books': Book.objects.filter(is_active=True).count(),
            'total_members': User.objects.filter(user_type='member', is_active_member=True).count(),
            'available_copies': BookCopy.objects.filter(status='available').count(),
            'active_borrowings': BorrowTransaction.objects.filter(status='active').count(),
            'recent_books': Book.objects.filter(is_active=True).order_by('-created_at')[:6],
        })
        
        # Add user-specific context if logged in
        if self.request.user.is_authenticated:
            context.update({
                'user_current_borrowings': BorrowTransaction.objects.filter(
                    user=self.request.user, 
                    status='active'
                ).count(),
                'user_reservations': self.request.user.reservations.filter(status='active').count(),
            })
        
        return context