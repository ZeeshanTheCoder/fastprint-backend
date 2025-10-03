from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0006_add_shipping_checkout_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookproject',
            name='shipping_rate',
            field=models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='bookproject',
            name='tax',
            field=models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='bookproject',
            name='product_price',
            field=models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True),
        ),
    ]


