from django.db import models
from django.conf import settings

class TrimSize(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class BindingType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class InteriorColor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class PaperType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CoverFinish(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class BookProject(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book_projects')
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=100)
    pdf_file = models.FileField(upload_to='books/pdfs/')
    cover_file = models.FileField(upload_to='books/covers/', blank=True, null=True)
    page_count = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Store these as strings, not foreign keys
    binding_type = models.CharField(max_length=100, blank=True, null=True)
    cover_finish = models.CharField(max_length=100, blank=True, null=True)
    interior_color = models.CharField(max_length=100, blank=True, null=True)
    paper_type = models.CharField(max_length=100, blank=True, null=True)
    trim_size = models.CharField(max_length=100, blank=True, null=True)

    # ✅ New field for cover design description
    cover_description = models.TextField(blank=True, null=True)

    # ===== Shipping and Checkout (saved at /shop) =====
    # Shipping address and account details
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    apt_floor = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=10, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    account_type = models.CharField(max_length=20, blank=True, null=True)
    has_resale_cert = models.BooleanField(default=False)

    # Shipping computation outcome
    shipping_rate = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    tax = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    courier_name = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery = models.CharField(max_length=100, blank=True, null=True)
    selected_service = models.TextField(blank=True, null=True)  # JSON or text description

    # Order/pricing summary
    product_quantity = models.PositiveIntegerField(blank=True, null=True)
    product_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    order_status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('paid', 'Paid')],
        default='draft',
        help_text='Order status: draft (unpaid/incomplete) or paid (completed)'
    )

    def __str__(self):
        return f"{self.title} by {self.user.email}"
