from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import LibraryBranch, LibrarySection

# Create basic placeholder views for library_branches app

class BranchListView(ListView):
    model = LibraryBranch
    template_name = 'library_branches/branch_list.html'
    context_object_name = 'branches'
    
    def get_queryset(self):
        return LibraryBranch.objects.filter(is_active=True).order_by('name')

class BranchDetailView(DetailView):
    model = LibraryBranch
    template_name = 'library_branches/branch_detail.html'
    context_object_name = 'branch'

class BranchBooksView(LoginRequiredMixin, TemplateView):
    template_name = 'library_branches/books.html'

class BranchSectionsView(LoginRequiredMixin, TemplateView):
    template_name = 'library_branches/sections.html'

class BranchManageView(LoginRequiredMixin, TemplateView):
    template_name = 'library_branches/manage.html'

class BranchCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'library_branches/create.html'

class BranchEditView(LoginRequiredMixin, TemplateView):
    template_name = 'library_branches/edit.html'

class BranchHoursView(LoginRequiredMixin, TemplateView):
    template_name = 'library_branches/hours.html'

class SectionListView(LoginRequiredMixin, TemplateView):
    template_name = 'library_branches/section_list.html'

class SectionCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'library_branches/section_create.html'

class SectionEditView(LoginRequiredMixin, TemplateView):
    template_name = 'library_branches/section_edit.html'
