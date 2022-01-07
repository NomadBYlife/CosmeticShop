from django.db import models


def calc_cart(cart):
    ca = cart.products.aggregate(models.Sum('final_price'), models.Count('id'))
    if ca.get('final_price__sum'):
        cart.final_price = ca['final_price__sum']
    else:
        cart.final_price = 0
    cart.total_products = ca['id__count']
    cart.save()
