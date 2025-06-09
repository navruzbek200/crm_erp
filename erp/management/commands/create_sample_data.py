from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from erp.models import *
from decimal import Decimal
import random
from datetime import datetime, timedelta
import uuid


class Command(BaseCommand):
    help = 'Create sample data for the clothing ERP system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('Created admin user (username: admin, password: admin123)')

        # Create categories
        categories = [
            'T-Shirts', 'Jeans', 'Dresses', 'Jackets', 'Shoes',
            'Accessories', 'Underwear', 'Sportswear', 'Formal Wear'
        ]
        for cat_name in categories:
            Category.objects.get_or_create(name=cat_name)

        # Create brands
        brands = [
            'Nike', 'Adidas', 'Zara', 'H&M', 'Uniqlo',
            'Levi\'s', 'Calvin Klein', 'Tommy Hilfiger', 'Gap'
        ]
        for brand_name in brands:
            Brand.objects.get_or_create(name=brand_name)

        # Create sizes
        sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
        for size_name in sizes:
            Size.objects.get_or_create(name=size_name)

        # Create colors
        colors = [
            ('Black', '#000000'), ('White', '#FFFFFF'), ('Red', '#FF0000'),
            ('Blue', '#0000FF'), ('Green', '#008000'), ('Yellow', '#FFFF00'),
            ('Pink', '#FFC0CB'), ('Gray', '#808080'), ('Brown', '#A52A2A'),
            ('Navy', '#000080')
        ]
        for color_name, hex_code in colors:
            Color.objects.get_or_create(name=color_name, defaults={'hex_code': hex_code})

        # Create products
        products_data = [
            ('Classic Cotton T-Shirt', 'T-Shirts', 'Nike', 29.99, 15.00),
            ('Slim Fit Jeans', 'Jeans', 'Levi\'s', 89.99, 45.00),
            ('Summer Dress', 'Dresses', 'Zara', 59.99, 30.00),
            ('Leather Jacket', 'Jackets', 'Calvin Klein', 199.99, 100.00),
            ('Running Shoes', 'Shoes', 'Adidas', 129.99, 65.00),
            ('Casual Sneakers', 'Shoes', 'Nike', 99.99, 50.00),
            ('Formal Shirt', 'Formal Wear', 'Tommy Hilfiger', 79.99, 40.00),
            ('Yoga Pants', 'Sportswear', 'Adidas', 49.99, 25.00),
            ('Winter Coat', 'Jackets', 'H&M', 149.99, 75.00),
            ('Basic Hoodie', 'T-Shirts', 'Uniqlo', 39.99, 20.00),
        ]

        for i, (name, cat_name, brand_name, price, cost) in enumerate(products_data):
            category = Category.objects.get(name=cat_name)
            brand = Brand.objects.get(name=brand_name)

            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'High quality {name.lower()} from {brand_name}',
                    'category': category,
                    'brand': brand,
                    'sku': f'SKU{1000 + i}',
                    'price': Decimal(str(price)),
                    'cost_price': Decimal(str(cost)),
                }
            )

            if created:
                sizes_list = Size.objects.all()
                colors_list = Color.objects.all()
                for size in random.sample(list(sizes_list), min(3, len(sizes_list))):
                    for color in random.sample(list(colors_list), min(2, len(colors_list))):
                        ProductVariant.objects.create(
                            product=product,
                            size=size,
                            color=color,
                            stock_quantity=random.randint(10, 100),
                            min_stock_level=5
                        )

        # Create customers
        customers_data = [
            ('John', 'Doe', 'john.doe@email.com', '+1234567890', 'M'),
            ('Jane', 'Smith', 'jane.smith@email.com', '+1234567891', 'F'),
            ('Mike', 'Johnson', 'mike.johnson@email.com', '+1234567892', 'M'),
            ('Sarah', 'Williams', 'sarah.williams@email.com', '+1234567893', 'F'),
            ('David', 'Brown', 'david.brown@email.com', '+1234567894', 'M'),
            ('Emily', 'Davis', 'emily.davis@email.com', '+1234567895', 'F'),
            ('Chris', 'Miller', 'chris.miller@email.com', '+1234567896', 'M'),
            ('Lisa', 'Wilson', 'lisa.wilson@email.com', '+1234567897', 'F'),
        ]

        for first, last, email, phone, gender in customers_data:
            Customer.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'phone': phone,
                    'gender': gender,
                    'address': f'{random.randint(100, 999)} Main St',
                    'city': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston']),
                    'postal_code': f'{random.randint(10000, 99999)}',
                }
            )

        # Create suppliers
        suppliers_data = [
            ('Fashion Wholesale Inc', 'John Manager', 'john@fashionwholesale.com'),
            ('Textile Suppliers Ltd', 'Sarah Director', 'sarah@textilesuppliers.com'),
            ('Global Apparel Co', 'Mike Sales', 'mike@globalapparel.com'),
        ]

        for name, contact, email in suppliers_data:
            Supplier.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'contact_person': contact,
                    'phone': f'+1234567{random.randint(100, 999)}',
                    'address': f'{random.randint(100, 999)} Business Ave',
                    'city': random.choice(['New York', 'Los Angeles', 'Chicago']),
                }
            )

        # Create sample orders
        customers = Customer.objects.all()
        variants = ProductVariant.objects.all()

        def generate_order_number():
            while True:
                number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
                if not Order.objects.filter(order_number=number).exists():
                    return number

        for _ in range(20):
            customer = random.choice(customers)
            order_number = generate_order_number()

            order = Order.objects.create(
                customer=customer,
                status=random.choice(['pending', 'processing', 'completed', 'shipped']),
                payment_status=random.choice(['pending', 'paid']),
                subtotal=Decimal('0'),
                total_amount=Decimal('0'),
                created_at=datetime.now() - timedelta(days=random.randint(1, 90)),
                order_number=order_number
            )

            # Add order items
            subtotal = Decimal('0')
            for _ in range(random.randint(1, 4)):
                variant = random.choice(variants)
                quantity = random.randint(1, 3)
                unit_price = variant.product.price
                total_price = quantity * unit_price

                OrderItem.objects.create(
                    order=order,
                    product_variant=variant,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price
                )
                subtotal += total_price

            order.subtotal = subtotal
            order.total_amount = subtotal
            order.save()

        # Create sample transactions
        for _ in range(50):
            Transaction.objects.create(
                transaction_type=random.choice(['sale', 'purchase', 'expense']),
                amount=Decimal(str(random.uniform(10, 500))),
                description=random.choice([
                    'Product Sale', 'Inventory Purchase', 'Office Supplies',
                    'Marketing Expense', 'Utility Bill', 'Equipment Purchase'
                ]),
                reference=f'REF{random.randint(1000, 9999)}',
                created_at=datetime.now() - timedelta(days=random.randint(1, 90))
            )

        self.stdout.write(self.style.SUCCESS('✅ Sample data created successfully!'))
        self.stdout.write('🔑 You can now login with username: admin, password: admin123')
