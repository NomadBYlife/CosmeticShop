# Generated by Django 4.0 on 2021-12-15 11:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CosmeticShop', '0002_alter_cart_final_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='CosmeticShop.customer', verbose_name='Покупатель'),
        ),
    ]
