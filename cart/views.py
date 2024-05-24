from django.shortcuts import render, get_object_or_404
from .cart import Cart
from main.models import Product
from django.http import JsonResponse
from django.contrib import messages

def cart_summary(request):
    #Get cart
    cart = Cart(request)
    cart_products = cart.get_prods
    totals = cart.cart_total()
    return render(request, "cart_summary.html", {"cart_products": cart_products, "totals": totals})

def cart_add(request):
    # get the cart
    cart = Cart(request)
    #test for POST
    if request.POST.get('action') == 'post':
        #Get Stuff
        product_id = int(request.POST.get('product_id'))
        #lookup product in db 
        product = get_object_or_404(Product, id=product_id)
        #Save to session
        cart.add(product=product)
        #Get Cart Quantity
        cart_quantity = cart.__len__()
        #Return Response 
        response = JsonResponse({'qty': cart_quantity})
        return response 


def cart_update(request):
    pass

def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        #GET STUFF
        product_id = int(request.POST.get('product_id'))
        #delete function in our cart 
        cart.delete(product=product_id)
        response = JsonResponse({'product': product_id})
        return response
