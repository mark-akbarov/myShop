from django.urls import reverse
from django.shortcuts import render, redirect
from orders.tasks import order_created
from orders.models import OrderItem
from orders.forms import OrderCreateForm
from orders.tasks import order_created
from cart.cart import Cart


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])

            cart.clear()
            #launch async task
            order_created.delay(order.id)
            #set the order in the session
            request.session['order_id'] = order.id
            #redirect for payment
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})