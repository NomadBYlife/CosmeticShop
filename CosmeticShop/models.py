from django.conf import settings
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe


class Condition(models.Model):
    """Консистенция(крем, сперй, масло)"""
    title = models.CharField(max_length=50, verbose_name='Консистенция')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Консистенция'
        verbose_name_plural = 'Консистенции'


class Effect(models.Model):
    """Эффект"""
    title = models.CharField(max_length=50, verbose_name='Эффект')
    slug = models.SlugField(verbose_name='slug')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Эффект'
        verbose_name_plural = 'Эффекты'


class ApplicationArea(models.Model):
    """Область применения"""
    title = models.CharField(max_length=100, verbose_name='Область применения')
    effect = models.ManyToManyField(Effect, related_name='AppArea', verbose_name='Эффект')
    slug = models.SlugField(verbose_name='slug')

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse('apparea_detail', kwargs={'apparea_slug': self.slug})

    class Meta:
        verbose_name = 'область применения'
        verbose_name_plural = 'области применения'


class Product(models.Model):
    """Продукт(средство косметическое)"""
    title = models.CharField(max_length=100, verbose_name='Название')
    app_area = models.ForeignKey(ApplicationArea, on_delete=models.CASCADE, verbose_name='Область применения')
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE, verbose_name='Консистенция')
    discription = models.TextField(max_length=2000, verbose_name='Описание', default='Описание появится позже')
    specifications = models.ForeignKey('Specifications', on_delete=models.CASCADE, verbose_name='Характеристики')
    slug = models.SlugField(verbose_name='Slug')
    stock = models.IntegerField(default=1, verbose_name='Наличие на складе')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    offer_week = models.BooleanField(default=False, verbose_name='Предложение недели')
    image_gallery = GenericRelation('ImageGallery')
    image = models.ImageField(upload_to='images/%Y/%m/%d/', blank=True, null=True, verbose_name='Главное изображение')

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'apparea_slug': self.app_area.slug, 'product_slug': self.slug})

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    @property
    def ct_model(self):  # наименование модели в ловеркейсе
        return self._meta.model_name



class Specifications(models.Model):
    """Характеристики"""
    manufacturer = models.CharField(max_length=200, verbose_name='Производитель')
    supplier = models.CharField(max_length=200, verbose_name='Поставщик')
    country = models.CharField(max_length=200, verbose_name='Страна производитель')
    brand = models.CharField(max_length=200, verbose_name='Брэнд')

    def __str__(self):
        return f'Характеристики для {self.product_set.first()}'

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'


class Customer(models.Model):
    """Покупатель"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Покупатель')
    is_active = models.BooleanField(default=True, verbose_name='Активен?')
    customer_orders = models.ManyToManyField('Order', blank=True, related_name='customer_related',
                                             verbose_name='Заказы')
    wishlist = models.ManyToManyField(Product, blank=True, related_name='wishlists', verbose_name='Ожидаемые')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.CharField(max_length=1000, verbose_name='Адрес', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username}'

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class CartProduct(models.Model):
    """Продукт корзины"""

    user = models.ForeignKey(Customer, verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id') # Product
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

    def __str__(self):
        return self.content_object.title

    def save(self, *args, **kwargs):
        self.final_price = self.quantity * self.content_object.price
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Продукт корзины'
        verbose_name_plural = 'Продукты корзины'


class Cart(models.Model):
    """Корзина"""
    owner = models.ForeignKey(Customer, verbose_name='Покупатель', on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(CartProduct, blank=True,  related_name='cart_related',
                                      verbose_name='Продукты для карзины')
    total_products = models.IntegerField(default=0, verbose_name='Кол-во товара')
    final_price = models.DecimalField(blank=True, null=True, max_digits=9, decimal_places=2, verbose_name='Общая цена')
    in_opder = models.BooleanField(default=False, verbose_name='В заказе')
    for_anonymous_user = models.BooleanField(default=False,verbose_name='Для анонима')

    def __str__(self):
        return f'{self.id}'

    def products_in_cart(self):
        return [c.content_object for c in self.products.all()]

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'




class Order(models.Model):
    """Заказ пользователя"""

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ получен покупателем'),
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель', related_name='orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=20, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True,  verbose_name='Корзина')
    address = models.CharField(max_length=1000, verbose_name='Адрес', blank=True, null=True)
    status = models.CharField(max_length=100, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, verbose_name='Тип заказа', choices=BUYING_TYPE_CHOICES,
                                   default=BUYING_TYPE_SELF)
    comment = models.CharField(max_length=300, verbose_name='Коментарий к заказу', blank=True, null=True)
    created = models.DateField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Notification(models.Model):
    """Уведомления"""
    recipient = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Получатель')
    text = models.TextField(verbose_name='Содержимое уведомления')
    read = models.BooleanField(default=False)


    def __str__(self):
        return f'Уведомление {self.id} для {self.recipient.user.username} '

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'


class ImageGallery(models.Model):
    """Галерея изображений"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to='images/%Y/%m/%d/', blank=True, null=True, verbose_name='Изображение')

    def __str__(self):
        return f'Изображение для {self.content_object} {self.object_id}'

    def image_url(self):
        return mark_safe(f'<img src="{self.image.url}" width="auto", height="100px">')

    class Meta:
        verbose_name = 'Галерея изображений'
        verbose_name_plural = verbose_name
