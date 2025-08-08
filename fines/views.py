from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create basic placeholder views for fines app

class FineListView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/list.html'

class FineDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/detail.html'

class PayFineView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/pay.html'

class FineHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/history.html'

class MembershipFeeListView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/membership_list.html'

class PayMembershipFeeView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/pay_membership.html'

class RenewMembershipView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/renew_membership.html'

class PriorityFeeListView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/priority_list.html'

class FineManageView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/manage.html'

class CreateFineView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/create.html'

class WaiveFineView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/waive.html'

class FineReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'fines/reports.html'
