from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product, Profile
import datetime

# Create your views here.

def payment_success(request):
    return render(request, 'payment/payment_success.html', {})

def checkout(request):
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals =cart.cart_total()

    if request.user.is_authenticated:
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)

        # Checkout as logged in user
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, 'payment/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})
    else:
        # Checkout as guest
        shipping_form = ShippingForm(request.POST or None,)
        return render(request, 'payment/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})
    
def billing_info(request):
    if request.POST:
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals =cart.cart_total()

        # Create a session with the shipping info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        # Check to see if user is logged in
        if request.user.is_authenticated:

            # Get the billing form
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_info': request.POST, 'billing_form': billing_form})
        else:
            # Get the billing form
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_info': request.POST, 'billing_form': billing_form})

        shipping_form = request.POST
        return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})
    else:
        messages.success(request, 'Access Denied')
        return redirect('home')

def process_order(request):
    if request.POST:
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()

        # Get billing info from the last page
        payment_form = PaymentForm(request.POST or None)
        # Get shipping session data
        my_shipping = request.session.get('my_shipping')

        # Gather order info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        # Create an order
        if request.user.is_authenticated:
            # Logged in user
            create_order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                email=email,
                shipping_address=shipping_address,
                amount_paid=amount_paid
            )

            # Add order items for authenticated user
            for product in cart_products:
                price = product.sale_price if product.is_sale else product.price
                quantity = quantities.get(str(product.id), 1)  # Default to 1 if not found
                
                OrderItem.objects.create(
                    order=create_order,
                    product=product,
                    user=request.user,
                    quantity=quantity,
                    price=price
                )

        # Clear the cart correctly
        if 'cart' in request.session:
            del request.session['cart']
        request.session.modified = True

        # Delete cart from database(old_cart field)
        current_user = Profile.objects.filter(user__id=request.user.id)
        # Delete shopping cart from database(old_cart field)
        current_user.update(old_cart = "")

        # If you need to clear other session data too:
        for key in list(request.session.keys()):
            if key == "session_key":  # Fixed typo in session_key
                del request.session[key]
            if key == "cart":
                del request.session[key]
            if key == "my_shipping":
                del request.session[key]

            messages.success(request, 'Order Placed Successfully')
            return redirect('home')
        else:
            # Guest user
            create_order = Order.objects.create(
                full_name=full_name,
                email=email,
                shipping_address=shipping_address,
                amount_paid=amount_paid
            )

            # Add order items for guest user
            for product in cart_products:
                price = product.sale_price if product.is_sale else product.price
                quantity = quantities.get(str(product.id), 1)  # Default to 1 if not found
                
                OrderItem.objects.create(
                    order=create_order,
                    product=product,
                    quantity=quantity,
                    price=price
                    # Note: no user field for guest orders
                )

            # Clear the cart correctly
        if 'cart' in request.session:
            del request.session['cart']
        request.session.modified = True

        # If you need to clear other session data too:
        for key in list(request.session.keys()):
            if key == "session_key":  # Fixed typo in session_key
                del request.session[key]
            if key == "cart":
                del request.session[key]
            if key == "my_shipping":
                del request.session[key]

            messages.success(request, 'Order Placed Successfully')
            return redirect('home')
    else:
        messages.success(request, 'Access Denied')
        return redirect('home')
    
def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            # Get the order
            order = Order.objects.filter(id=num)
            # Grab date and time
            now = datetime.datetime.now()
            # Update the order status
            order.update(shipped = True, date_shipped = now)
            # Redirect to the dashboard
            messages.success(request, 'Shipping status updated')
            return redirect('home')
        return render(request, 'payment/shipped_dash.html', {'orders': orders})
    else:
        messages.success(request, 'Access Denied')
        return redirect('home')

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            # Get the order
            order = Order.objects.filter(id=num)
            # Grab date and time
            now = datetime.datetime.now()
            # Update the order status
            order.update(shipped = True, date_shipped = now)
            # Redirect to the dashboard
            messages.success(request, 'Shipping status updated')
            return redirect('home')
        return render(request, 'payment/not_shipped_dash.html', {'orders': orders})
    else:
        messages.success(request, 'Access Denied')
        return redirect('home')
    
def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # Get the order
        order = Order.objects.get(id=pk)

        # Get the order items
        items = OrderItem.objects.filter(order=order)

        if request.POST:
            status = request.POST['shipping_status']
            # Check if true or false
            if status == 'true':
                # Get the order
                order = Order.objects.filter(id=pk)
                # Update the order status
                now = datetime.datetime.now()
                order.update(shipped = True, date_shipped = now)
            else:
                # Get the order
                order = Order.objects.filter(id=pk)
                # Update the order
                order.update(shipped = False)

            messages.success(request, 'Order Status Updated')
            return redirect('home')
        return render(request, 'payment/orders.html', {'order': order, 'items': items})