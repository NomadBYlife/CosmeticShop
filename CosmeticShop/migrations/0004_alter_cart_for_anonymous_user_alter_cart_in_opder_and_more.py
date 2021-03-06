# Generated by Django 4.0 on 2021-12-16 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CosmeticShop', '0003_alter_cart_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='for_anonymous_user',
            field=models.BooleanField(default=False, verbose_name='Для анонима'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='in_opder',
            field=models.BooleanField(default=False, verbose_name='В заказе'),
        ),
        migrations.AlterField(
            model_name='imagegallery',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='media/images/%Y/%m/%d/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='media/images/%Y/%m/%d/', verbose_name='Изображение'),
        ),
    ]
