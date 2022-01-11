from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline  # only for content_type

from CosmeticShop.models import *


class EffectInline(admin.TabularInline):
    model = ApplicationArea.effect.through


class ImageGalleryInline(GenericTabularInline):
    model = ImageGallery
    readonly_fields = ('image_url',)


class ApplicationAreaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = [EffectInline]
    exclude = ('effect',)


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')
    inlines = [ImageGalleryInline]


class EffectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'total_products', 'final_price', 'in_opder', 'for_anonymous_user')
    list_display_links = ('id', 'total_products')


admin.site.register(Condition)
admin.site.register(ApplicationArea, ApplicationAreaAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Effect, EffectAdmin)
admin.site.register(Specifications)
admin.site.register(Customer)
admin.site.register(CartProduct)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order)
admin.site.register(Notification)
admin.site.register(ImageGallery)
