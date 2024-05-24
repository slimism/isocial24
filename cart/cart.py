from main.models import Product, Profile
class Cart():
    def __init__(self, request):
        self.session = request.session
        #GET Request
        self.request = request

        #Get current session Key
        cart = self.session.get('session_key')

        # If the user is new, no session key, create one
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        #Make sure cart is available on all pages of site
        self.cart = cart 

    def db_add(self, product):
        product_id = str(product)
        #Logic 
        if product_id in self.cart:
            pass 
        else:
            #self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = 1

        self.session.modified = True

        #Logged in User
        if self.request.user.is_authenticated:
            #Get current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            #Covert Dictionary to double quotation 
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #save carty to profile model 
            current_user.update(old_cart=str(carty))

    
    def add(self, product):
        product_id = str(product.id)
        #Logic 
        if product_id in self.cart:
            pass 
        else:
            #self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = 1

        self.session.modified = True

        #Logged in User
        if self.request.user.is_authenticated:
            #Get current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            #Covert Dictionary to double quotation 
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #save carty to profile model 
            current_user.update(old_cart=str(carty))
    
    def __len__(self):
        return len(self.cart)
    
    def get_prods(self):
        #Get ids from cart
        product_ids = self.cart.keys()
        #Look up products in database model 
        products = Product.objects.filter(id__in=product_ids)

        return products
    
    def delete(self, product):
        product_id = str(product)
        # delete from dictionary / cart 
        if product_id in self.cart:
            del self.cart[product_id]
        self.session.modified = True
        #Logged in User
        if self.request.user.is_authenticated:
            #Get current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            #Covert Dictionary to double quotation 
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #save carty to profile model 
            current_user.update(old_cart=str(carty))

    def cart_total (self):
        #Get product ids
        product_ids = self.cart.keys()
        #look up keys in products database model
        products = Product.objects.filter(id__in=product_ids)
        #get quantities
        quantities = self.cart
        total = 0
        for key, value in quantities.items():
            #convert key string into int 
            key = int(key)
            for product in products:
                if product.id == key:
                    total = total + (product.price)
        return total
