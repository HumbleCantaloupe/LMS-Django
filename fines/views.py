from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from .models import Fine, FineType, FinePayment
from accounts.models import User

class FineListView(LoginRequiredMixin, ListView):
    model = Fine
    template_name = 'fines/fine_list.html'
    context_object_name = 'fines'
    paginate_by = 10
    
    def get_queryset(self):
        # Show current user's fines only
        return Fine.objects.filter(user=self.request.user).order_by('-issued_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_fines = Fine.objects.filter(user=self.request.user)
        context['total_fines'] = user_fines.aggregate(total=Sum('amount'))['total'] or 0
        context['paid_fines'] = user_fines.filter(status='paid').aggregate(total=Sum('amount_paid'))['total'] or 0
        context['pending_fines'] = user_fines.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0
        return context

class FineDetailView(LoginRequiredMixin, DetailView):
    model = Fine
    template_name = 'fines/detail.html'
    context_object_name = 'fine'
    
    def get_queryset(self):
        # Users can only see their own fines
        return Fine.objects.filter(user=self.request.user)

class PayFineView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/pay_fine.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fine_id = self.kwargs.get('pk')
        context['fine'] = get_object_or_404(Fine, pk=fine_id, user=self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        fine_id = self.kwargs.get('pk')
        fine = get_object_or_404(Fine, pk=fine_id, user=request.user)
        
        if fine.status == 'paid':
            messages.error(request, 'This fine has already been paid.')
            return redirect('fines:fine_list')
        
        # Simulate payment processing
        payment_amount = fine.amount - fine.amount_paid
        
        # Create payment record
        payment = FinePayment.objects.create(
            fine=fine,
            amount=payment_amount,
            payment_method='online',  # Default for web payments
            processed_by=request.user
        )
        
        # Update fine
        fine.amount_paid = fine.amount
        fine.status = 'paid'
        fine.save()
        
        messages.success(request, f'Payment of ${payment_amount:.2f} processed successfully!')
        return redirect('fines:fine_list')

class FineHistoryView(LoginRequiredMixin, ListView):
    model = Fine
    template_name = 'fines/payment_history.html'
    context_object_name = 'fines'
    paginate_by = 20
    
    def get_queryset(self):
        return Fine.objects.filter(user=self.request.user).order_by('-issued_date')

class MembershipFeeListView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/membership.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['membership_active'] = user.is_active_member
        context['membership_expires'] = user.membership_expiry
        return context

class PayMembershipFeeView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/pay_membership.html'

class RenewMembershipView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/membership_renewal.html'
    
    def post(self, request, *args, **kwargs):
        user = request.user
        # Simulate membership renewal
        from datetime import timedelta
        from django.utils import timezone
        
        user.membership_expiry = timezone.now() + timedelta(days=365)
        user.is_active_member = True
        user.save()
        
        messages.success(request, 'Membership renewed successfully for 1 year!')
        return redirect('fines:membership_list')

class PriorityFeeListView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/priority_reservations.html'

class FineManageView(LoginRequiredMixin, ListView):
    model = Fine
    template_name = 'fines/librarian_user_fines.html'
    context_object_name = 'fines'
    paginate_by = 20
    
    def get_queryset(self):
        # For librarians to manage all fines
        return Fine.objects.all().order_by('-issued_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_fines'] = Fine.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['pending_fines'] = Fine.objects.filter(status='pending').count()
        context['paid_fines'] = Fine.objects.filter(status='paid').count()
        return context

class CreateFineView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/create.html'
    
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        fine_type_id = request.POST.get('fine_type_id')
        amount = request.POST.get('amount')
        description = request.POST.get('description', '')
        
        if user_id and fine_type_id and amount:
            user = get_object_or_404(User, pk=user_id)
            fine_type = get_object_or_404(FineType, pk=fine_type_id)
            
            from datetime import timedelta
            
            fine = Fine.objects.create(
                user=user,
                fine_type=fine_type,
                amount=amount,
                due_date=timezone.now() + timedelta(days=30),
                description=description,
                issued_by=request.user
            )
            
            messages.success(request, f'Fine created successfully for {user.username}')
            return redirect('fines:manage')
        
        messages.error(request, 'Please fill all required fields')
        return redirect('fines:create')

class WaiveFineView(LoginRequiredMixin, TemplateView):
    
    def post(self, request, *args, **kwargs):
        fine_id = self.kwargs.get('pk')
        fine = get_object_or_404(Fine, pk=fine_id)
        
        fine.status = 'waived'
        fine.save()
        
        messages.success(request, f'Fine #{fine.id} has been waived successfully')
        return redirect('fines:manage')

class FineReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Summary statistics
        context['total_fines'] = Fine.objects.count()
        context['total_amount'] = Fine.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['paid_amount'] = Fine.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
        context['pending_fines'] = Fine.objects.filter(status='pending').count()
        context['paid_fines'] = Fine.objects.filter(status='paid').count()
        context['waived_fines'] = Fine.objects.filter(status='waived').count()
        
        # Recent fines
        context['recent_fines'] = Fine.objects.order_by('-issued_date')[:10]
        
        return context
