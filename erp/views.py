from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, Case, When, DecimalField, F
from django.utils import timezone
from datetime import timedelta
from .models import *
import json


@login_required
def dashboard(request):
    current_month = timezone.now().replace(day=1)

    # Financial metrics
    total_sales = Transaction.objects.filter(
        transaction_type='sale',
        created_at__gte=current_month
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_expenses = Transaction.objects.filter(
        transaction_type__in=['purchase', 'expense'],
        created_at__gte=current_month
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_profit = total_sales - total_expenses

    # Statistics
    total_orders = Order.objects.filter(created_at__gte=current_month).count()
    pending_orders = Order.objects.filter(status='pending').count()
    completed_orders = Order.objects.filter(status='completed', created_at__gte=current_month).count()
    total_products = Product.objects.filter(is_active=True).count()
    total_customers = Customer.objects.filter(is_active=True).count()
    new_customers = Customer.objects.filter(created_at__gte=current_month).count()

    low_stock_count = ProductVariant.objects.filter(
        stock_quantity__lte=F('min_stock_level')
    ).count()

    # Recent data
    recent_transactions = Transaction.objects.select_related('order').order_by('-created_at')[:5]
    low_stock_items = ProductVariant.objects.filter(
        stock_quantity__lte=F('min_stock_level')
    ).select_related('product', 'size', 'color')[:5]

    context = {
        'total_sales': total_sales,
        'total_expenses': total_expenses,
        'total_profit': total_profit,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_customers': total_customers,
        'new_customers': new_customers,
        'recent_transactions': recent_transactions,
        'low_stock_items': low_stock_items,
    }

    return render(request, 'erp/dashboard.html', context)


@login_required
def products(request):
    products = Product.objects.select_related('category', 'brand').prefetch_related('variants')

    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search) |
            Q(category__name__icontains=search) |
            Q(brand__name__icontains=search)
        )

    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    status = request.GET.get('status')
    if status == 'active':
        products = products.filter(is_active=True)
    elif status == 'inactive':
        products = products.filter(is_active=False)

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'search': search,
        'selected_category': category_id,
        'selected_status': status,
    }

    return render(request, 'erp/products.html', context)


@login_required
def customers(request):
    customers = Customer.objects.annotate(
        order_count=Count('orders'),
        total_spent=Sum(
            Case(
                When(orders__status='completed', then='orders__total_amount'),
                default=0,
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )
    ).order_by('-created_at')

    search = request.GET.get('search')
    if search:
        customers = customers.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(city__icontains=search)
        )

    status = request.GET.get('status')
    if status == 'active':
        customers = customers.filter(is_active=True)
    elif status == 'inactive':
        customers = customers.filter(is_active=False)

    context = {
        'customers': customers,
        'search': search,
        'selected_status': status,
    }

    return render(request, 'erp/customers.html', context)


@login_required
def orders(request):
    orders = Order.objects.select_related('customer').prefetch_related('items__product_variant__product')

    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(customer__email__icontains=search)
        )

    context = {
        'orders': orders,
        'search': search,
        'selected_status': status,
        'status_choices': Order.STATUS_CHOICES,
    }

    return render(request, 'erp/orders.html', context)


@login_required
def inventory(request):
    variants = ProductVariant.objects.select_related('product', 'size', 'color', 'product__category')

    low_stock = request.GET.get('low_stock')
    if low_stock:
        variants = variants.filter(stock_quantity__lte=F('min_stock_level'))

    search = request.GET.get('search')
    if search:
        variants = variants.filter(
            Q(product__name__icontains=search) |
            Q(product__sku__icontains=search) |
            Q(size__name__icontains=search) |
            Q(color__name__icontains=search)
        )

    context = {
        'variants': variants,
        'search': search,
        'low_stock_filter': low_stock,
    }

    return render(request, 'erp/inventory.html', context)


@login_required
def reports(request):
    current_month = timezone.now().replace(day=1)

    # Monthly sales (last 6 months)
    monthly_sales = []
    for i in range(6):
        date = current_month - timedelta(days=30 * i)
        sales = Transaction.objects.filter(
            transaction_type='sale',
            created_at__year=date.year,
            created_at__month=date.month
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_sales.append({
            'month': date.strftime('%b %Y'),
            'sales': float(sales)
        })
    monthly_sales.reverse()

    # Top selling products
    top_products = OrderItem.objects.values(
        'product_variant__product__name'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_sold')[:10]

    # Top customers
    top_customers = Customer.objects.annotate(
        total_spent=Sum(
            Case(
                When(orders__status='completed', then='orders__total_amount'),
                default=0,
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ),
        order_count=Count('orders')
    ).filter(total_spent__gt=0).order_by('-total_spent')[:10]

    context = {
        'monthly_sales': json.dumps(monthly_sales),
        'top_products': top_products,
        'top_customers': top_customers,
    }

    return render(request, 'erp/reports.html', context)


@login_required
def transactions(request):
    transactions = Transaction.objects.select_related('order', 'order__customer').order_by('-created_at')

    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)

    search = request.GET.get('search')
    if search:
        transactions = transactions.filter(
            Q(description__icontains=search) |
            Q(reference__icontains=search) |
            Q(order__order_number__icontains=search)
        )

    context = {
        'transactions': transactions,
        'search': search,
        'selected_type': transaction_type,
        'transaction_types': Transaction.TRANSACTION_TYPES,
    }

    return render(request, 'erp/transactions.html', context)


@login_required
def suppliers(request):
    suppliers = Supplier.objects.order_by('name')

    search = request.GET.get('search')
    if search:
        suppliers = suppliers.filter(
            Q(name__icontains=search) |
            Q(contact_person__icontains=search) |
            Q(email__icontains=search) |
            Q(city__icontains=search)
        )

    status = request.GET.get('status')
    if status == 'active':
        suppliers = suppliers.filter(is_active=True)
    elif status == 'inactive':
        suppliers = suppliers.filter(is_active=False)

    context = {
        'suppliers': suppliers,
        'search': search,
        'selected_status': status,
    }

    return render(request, 'erp/suppliers.html', context)