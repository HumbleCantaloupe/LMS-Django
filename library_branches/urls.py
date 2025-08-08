from django.urls import path
from . import views

app_name = 'library_branches'

urlpatterns = [
    # Branch information
    path('', views.BranchListView.as_view(), name='branch_list'),
    path('<int:pk>/', views.BranchDetailView.as_view(), name='branch_detail'),
    path('<int:pk>/books/', views.BranchBooksView.as_view(), name='books'),
    path('<int:pk>/sections/', views.BranchSectionsView.as_view(), name='sections'),
    
    # Branch management (for administrators)
    path('manage/', views.BranchManageView.as_view(), name='manage'),
    path('create/', views.BranchCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.BranchEditView.as_view(), name='edit'),
    path('<int:pk>/hours/', views.BranchHoursView.as_view(), name='hours'),
    
    # Section management
    path('sections/', views.SectionListView.as_view(), name='section_list'),
    path('sections/create/', views.SectionCreateView.as_view(), name='section_create'),
    path('sections/<int:pk>/edit/', views.SectionEditView.as_view(), name='section_edit'),
]
