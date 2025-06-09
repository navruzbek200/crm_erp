from django.contrib import admin
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order']
    list_editable = ['sort_order']
    ordering = ['sort_order']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code']
    search_fields = ['name']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['size', 'color', 'stock_quantity', 'min_stock_level']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'brand', 'price', 'is_active']
    list_filter = ['category', 'brand', 'is_active', 'created_at']
    search_fields = ['name', 'sku']
    list_editable = ['price', 'is_active']
    inlines = [ProductVariantInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'color', 'stock_quantity', 'min_stock_level', 'low_stock_status']
    list_filter = ['product__category', 'size', 'color']
    search_fields = ['product__name', 'product__sku']
    list_editable = ['stock_quantity', 'min_stock_level']

    def low_stock_status(self, obj):
        if obj.is_low_stock():
            return "⚠️ Low Stock"
        return "✅ In Stock"

    low_stock_status.short_description = "Stock Status"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'city', 'get_order_count', 'get_total_spent_display', 'is_active']
    list_filter = ['gender', 'city', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']

    def get_order_count(self, obj):
        return obj.get_total_orders()

    get_order_count.short_description = "Total Orders"

    def get_total_spent_display(self, obj):
        return f"${obj.get_total_spent():.2f}"

    get_total_spent_display.short_description = "Total Spent"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'payment_status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name', 'customer__email']
    list_editable = ['status', 'payment_status']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'created_at', 'updated_at']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone', 'city', 'is_active']
    list_filter = ['city', 'is_active', 'created_at']
    search_fields = ['name', 'contact_person', 'email']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_type', 'amount', 'description', 'reference', 'order', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['description', 'reference', 'order__order_number']
    readonly_fields = ['created_at']