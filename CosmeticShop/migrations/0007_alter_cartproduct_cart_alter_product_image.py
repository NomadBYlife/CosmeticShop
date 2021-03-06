# Generated by Django 4.0 on 2021-12-23 20:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CosmeticShop', '0006_alter_customer_wishlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartproduct',
            name='cart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='CosmeticShop.cart', verbose_name='Корзина'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/%Y/%m/%d/', verbose_name='Главное изображение'),
        ),
    ]
