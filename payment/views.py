from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib import messages
from django.contrib.auth.models import User
from main.models import Product, Profile
from django.core.paginator import Paginator
import datetime

#import paypal
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid #unique user id for duplicate orders

def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        #Get the order
        order = Order.objects.get(id=pk)
        #Get the order item 
        items = OrderItem.objects.filter(order=pk)
        if request.POST:
            status = request.POST['shipping_status']
            #Check if True or false 
            if status == "true":
                order = Order.objects.filter(id=pk)
                #Update Status 
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)
            else: 
                order = Order.objects.filter(id=pk)
                #Update Status 
                order.update(shipped=False)
            messages.success(request, "Shipping Status Updated")
            return redirect ('home')
        return render(request, "payment/orders.html", {"order": order, "items": items}) 
    else:
        messages.error(request,"Access Denied")
        return redirect('home')


def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            #Get Order
            order = Order.objects.filter(id=num)
            #Check if True or false 
            now = datetime.datetime.now()
            order.update(shipped=True, date_shipped=now) 
            messages.success(request, "Shipping Status Updated")

        paginator = Paginator(orders, 20)  # Show 20 orders per page

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, "payment/not_shipped_dash.html", {"page_obj": page_obj})
    else:
        messages.error(request, "Access Denied")
        return redirect('home')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)
            #Check if True or false 
            now = datetime.datetime.now()
            order.update(shipped=False) 
            messages.success(request, "Shipping Status Updated")
        paginator = Paginator(orders, 20)  # Show 20 orders per page

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, "payment/shipped_dash.html", {"page_obj": page_obj})
    else:
        messages.error(request,"Access Denied")
        return redirect('home')

def process_order(request):
    if request.POST:
         #Get cart
        cart = Cart(request)
        cart_products = cart.get_prods
        totals = cart.cart_total()
        #Get Billing info from last page 
        payment_form = PaymentForm(request.POST or None)
        #Get Shipping Session Data
        my_shipping = request.session.get('my_shipping')

        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        #Create Shipping address from session info 
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}\n"
        amount_paid = totals

        #create an order
        if request.user.is_authenticated:
            user = request.user
            #Create Order 
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            #Add Order Items 
            #Get Order ID 
            order_id =  create_order.pk
            #Get Product Info 
            for product in cart_products():
                #Get Product ID 
                product_id = product.id
                #Get Product price
                price = product.price

                create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, price=price)
                create_order_item.save()

            #Delete our cart 
            for key in list(request.session.keys()):
                if key == "session_key":
                    #Delete Key 
                    del request.session[key]
            #Delete old cart field from data base 
            current_user = Profile.objects.filter(user__id=request.user.id)
            #Delete shopping cart in data base 
            current_user.update(old_cart="")


            messages.success(request,"Orders Placed")
            return redirect('home')
        else: 
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            
            #Add Order Items 
            #Get Order ID 
            order_id =  create_order.pk
            #Get Product Info 
            for product in cart_products():
                #Get Product ID 
                product_id = product.id
                #Get Product price
                price = product.price

                create_order_item = OrderItem(order_id=order_id, product_id=product_id, price=price)
                create_order_item.save()
                
            #Delete our cart 
            for key in list(request.session.keys()):
                if key == "session_key":
                    #Delete Key 
                    del request.session[key]
                    
            messages.success(request,"Orders Placed")
            return redirect('home')
    else:
        messages.error(request,"You must be logged in")
        return redirect('home')
        

def billing_info(request):
    if request.POST:

        #Get cart
        cart = Cart(request)
        cart_products = cart.get_prods
        totals = cart.cart_total()

        #Create a session with Shipping Info 
        my_shipping = request.POST 
        request.session['my_shipping'] = my_shipping
        #Get Host
        host = request.get_host()
        #Create Paypal Form dictionary

        paypal_dict = {
            'business' : settings.PAYPAL_RECEIVER_EMAIL, 
            'amount' : totals,
            'item_name' : 'Package Order',
            'no_shipping': '2',
            'invoice' : str(uuid.uuid4()),
            'currency_code' : 'USD',
            'notify_url' : 'https://{}{}'.format(host, reverse("paypal-ipn")),
            'return_url' : 'https://{}{}'.format(host, reverse("payment_success")),
            'cancel_url' : 'https://{}{}'.format(host, reverse("payment_failed")),
        }

        #Create Paypal Button
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)



        #Check to see if logged in 
        if request.user.is_authenticated:
            #Get billing form 
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {"paypal_form" : paypal_form, "cart_products": cart_products, "totals": totals, "shipping_info":request.POST, "billing_form":billing_form })
        else:
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {"paypal_form" : paypal_form, "cart_products": cart_products, "totals": totals, "shipping_info":request.POST, "billing_form":billing_form })
        shipping_form = request.POST
        return render(request, "payment/billing_info.html", {"cart_products": cart_products, "totals": totals, "shipping_form":shipping_form })
    else:
        messages.error(request,"You must be logged in")
        return redirect('home')

def payment_success(request):
    return render (request, "payment/payment_success.html", {})


def payment_failed(request):
    return render (request, "payment/payment_failed.html", {})

def checkout(request):
    #Get cart
    cart = Cart(request)
    cart_products = cart.get_prods
    totals = cart.cart_total()

    if request.user.is_authenticated:
        #Checkout as Authenticated User
        #Get Shipping User
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        #Get Shipping Form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, "payment/checkout.html", {"cart_products": cart_products, "totals": totals, "shipping_form":shipping_form })
    else:
        #Checkout as Guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, "payment/checkout.html", {"cart_products": cart_products, "totals": totals, "shipping_form":shipping_form })
    
