from .cart import Cart

#Create context processor so our cart works on all pages 

def cart(request):
    #Return default data
    return {'cart': Cart(request)}