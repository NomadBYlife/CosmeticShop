from django import views
from django.contrib.auth import authenticate, login, logout
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import DetailView
from django.contrib import messages
from django.db import transaction

from CosmeticShop.forms import RegisterUserForm, LoginUserForm, OrderForm
from CosmeticShop.models import ApplicationArea, Product, Customer, Cart, CartProduct
from CosmeticShop.mixins import CartMixin
from CosmeticShop.utils import calc_cart


class BaseView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        products = Product.objects.all().order_by('-id')
        apparea = ApplicationArea.objects.all()
        context = {
            'apparea': apparea,
            'products': products,
            'cart': self.cart
        }
        return render(request, 'CosmeticShop/layout.html', context)


class AppAreaDetail(CartMixin, DetailView):
    # model = ApplicationArea
    # template_name = 'CosmeticShop/apparea.html'
    # slug_url_kwarg = 'apparea_slug'
    # context_object_name = 'apparea'

    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(app_area__slug=kwargs['apparea_slug']).order_by('-id')
        apparea = ApplicationArea.objects.all()
        context = {
            'products': products,
            'apparea': apparea,
            'cart': self.cart
        }
        return render(request, 'CosmeticShop/apparea.html', context)


class ProductDetail(CartMixin, DetailView):
    model = Product
    template_name = 'CosmeticShop/product.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'


class LoginUserView(View):

    def get(self, request):
        form = LoginUserForm()
        context = {'form': form}
        return render(request, 'CosmeticShop/login.html', context)

    def post(self, request):
        form = LoginUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')

        context = {
            'form': form
        }
        return render(request, 'CosmeticShop/login.html', context)


class RegisterUserView(View):

    def get(self, request):
        form = RegisterUserForm()
        context = {'form': form}
        return render(request, 'CosmeticShop/register.html', context)

    def post(self, request):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user,
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
            )
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)

            return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'CosmeticShop/register.html', context)


def logout_user(request):
    logout(request)
    return redirect('/')


class Account(CartMixin, View):
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.filter(user=request.user).first()
        context = {
            'cart': self.cart,
            'customer': customer

        }
        return render(request, 'CosmeticShop/account.html', context)


class CartView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        context = {'cart': self.cart}
        return render(request, 'CosmeticShop/cart.html', context)


class CartAdd(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner,
            cart=self.cart,
            content_type=content_type,
            object_id=product.id)
        if created:
            self.cart.products.add(cart_product)
        calc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Товар успешно добавлен')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class CartDelete(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model = kwargs.get('ct_model')
        product_slug = kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner,
            cart=self.cart,
            content_type=content_type,
            object_id=product.id)
        self.cart.products.remove(cart_product)
        cart_product.delete()
        calc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Товар успешно удален')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class CartChangeQty(CartMixin, View):

    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner,
            cart=self.cart,
            content_type=content_type,
            object_id=product.id)
        qty = int(request.POST.get('quantity'))
        cart_product.quantity = qty
        cart_product.save()
        calc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Количество успешно изменено')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class WishlistAdd(View):

    @staticmethod
    def get(request, *args, **kwargs):
        product = Product.objects.get(id=kwargs['product_id'])
        customer = Customer.objects.get(user=request.user)
        customer.wishlist.add(product)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class WishlistDelete(View):

    @staticmethod
    def get(request, *args, **kwargs):
        product = Product.objects.get(id=kwargs['product_id'])
        customer = Customer.objects.get(user=request.user)
        customer.wishlist.remove(product)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class OrderView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        context = {
            'form': form,
            'cart': self.cart
        }
        return render(request, 'CosmeticShop/order.html', context)


class MakeOrderView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            out_of_stock = []
            more_than_stok = []
            out_of_stock_massage = ''
            more_than_stok_massage = ''
            for i in self.cart.products.all():
                if not i.content_object.stock:
                    out_of_stock.append(
                        i.content_object.title
                    )
                if i.content_object.stock and i.content_object.stock < i.quantity:
                    more_than_stok.append({
                        'product': i.content_object.title,
                        'stock': i.content_object.stock,
                        'quantity': i.quantity
                    })
            if out_of_stock:
                out_of_stock_product = ', '.join(out_of_stock)
                out_of_stock_massage = f'Товара нет в наличии: {out_of_stock_product}. \n'

            if more_than_stok:
                for i in more_than_stok:
                    more_than_stok_massage += f'Товар: {i["product"]}. ' \
                                              f'В наличии {i["stock"]}. Заказано {i["quantity"]} \n'
            error_message_for_customer = ''
            if out_of_stock:
                error_message_for_customer = out_of_stock_massage + '\n'
            if more_than_stok_massage:
                error_message_for_customer += more_than_stok_massage + '\n'

            if error_message_for_customer:
                messages.add_message(request, messages.INFO, error_message_for_customer)
                return HttpResponseRedirect('/order/')

            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()

            self.cart.in_opder = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.customer_orders.add(new_order)

            for i in self.cart.products.all():
                i.content_object.stock -= i.quantity
                i.content_object.save()

            messages.add_message(request, messages.INFO, 'Спасибо за заказ с вами звяжутся')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/order/')
