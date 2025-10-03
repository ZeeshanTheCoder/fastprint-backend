from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0005_remove_bookproject_contact_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookproject',
            name='first_name',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='last_name',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='company',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='address',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='apt_floor',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='country',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='state',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='city',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='postal_code',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='phone_number',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='account_type',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='has_resale_cert',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='shipping_rate',
            field=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='tax',
            field=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='courier_name',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='estimated_delivery',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='selected_service',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='product_quantity',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='product_price',
            field=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookproject',
            name='subtotal',
            field=models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True),
        ),
    ]


