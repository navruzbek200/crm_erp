from django.urls import path
from . import views

app_name = 'erp'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.products, name='products'),
    path('customers/', views.customers, name='customers'),
    path('orders/', views.orders, name='orders'),
    path('inventory/', views.inventory, name='inventory'),
    path('reports/', views.reports, name='reports'),
    path('transactions/', views.transactions, name='transactions'),
    path('suppliers/', views.suppliers, name='suppliers'),
]