# Generated by Django 5.0.1 on 2024-02-27 06:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_alter_order_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='shipping_address',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='order.shippingaddress'),
        ),
    ]