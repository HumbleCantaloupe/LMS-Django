from django.urls import path
from . import views

app_name = 'fines'

urlpatterns = [
    # Fine management
    path('', views.FineListView.as_view(), name='fine_list'),
    path('<int:pk>/', views.FineDetailView.as_view(), name='fine_detail'),
    path('pay/<int:pk>/', views.PayFineView.as_view(), name='pay'),
    path('history/', views.FineHistoryView.as_view(), name='history'),
    
    # Membership fees
    path('membership/', views.MembershipFeeListView.as_view(), name='membership_list'),
    path('membership/pay/<int:pk>/', views.PayMembershipFeeView.as_view(), name='pay_membership'),
    path('membership/renew/', views.RenewMembershipView.as_view(), name='renew_membership'),
    
    # Priority reservation fees
    path('priority/', views.PriorityFeeListView.as_view(), name='priority_list'),
    
    # Librarian functions
    path('manage/', views.FineManageView.as_view(), name='manage'),
    path('create/', views.CreateFineView.as_view(), name='create'),
    path('<int:pk>/waive/', views.WaiveFineView.as_view(), name='waive'),
    path('reports/', views.FineReportsView.as_view(), name='reports'),
]
