from django.views import View
from django.views.generic.detail import SingleObjectMixin

from .models import Cart, Customer


class CartMixin(SingleObjectMixin, View):

    def dispatch(self, request, *args, **kwargs):
        cart = None
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                Customer.objects.create(user=request.user)
            cart = Cart.objects.filter(owner=customer, in_opder=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context
