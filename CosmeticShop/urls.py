from django.urls import path
from CosmeticShop.views import *


urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logour/', logout_user, name='logout'),
    path('account/', Account.as_view(), name='account'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart_add/<str:ct_model>/<str:slug>', CartAdd.as_view(), name='cart_add'),
    path('cart_delete/<str:ct_model>/<str:slug>', CartDelete.as_view(), name='cart_delete'),
    path('cart_change/<str:ct_model>/<str:slug>', CartChangeQty.as_view(), name='cart_change'),
    path('wishlist_add/<int:product_id>', WishlistAdd.as_view(), name='wishlist_add'),
    path('wishlist_delete/<int:product_id>', WishlistDelete.as_view(), name='wishlist_delete'),
    path('order/', OrderView.as_view(), name='order'),
    path('makeorder/', MakeOrderView.as_view(), name='makeorder'),

    path('<str:apparea_slug>/', AppAreaDetail.as_view(), name='apparea_detail'),
    path('<str:apparea_slug>/<str:product_slug>/', ProductDetail.as_view(), name='product_detail'),
]