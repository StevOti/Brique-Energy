from store.models import Product, Profile

class Cart():
    def __init__(self, request):
        self.session = request.session

        # Get request
        self.request = request

        # Get the current session key
        cart = self.session.get('session_key')

        # If there is no session key, create one
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Make sure the cart is available on all pages of the site
        self.cart = cart

    def db_add(self, product, quantity):
        product_id = str(product)
        product_qty = str(quantity)

        if product_id in self.cart:
            pass
        else:
            self.cart[product_id] = int(product_qty)

        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.get(user__id=self.request.user.id)
            # Convert the cart to a string
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            # Save the cart to the user profile model
            current_user.old_cart = carty  # Directly assign the value
            current_user.save()  # Save the changes
        

    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = str(quantity)

        if product_id in self.cart:
            pass
        else:
            self.cart[product_id] = int(product_qty)

        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.get(user__id=self.request.user.id)
            # Convert the cart to a string
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            # Save the cart to the user profile model
            current_user.old_cart = carty  # Directly assign the value
            current_user.save()  # Save the changes

    def cart_total(self):
    # Get product ids from cart
        product_ids = self.cart.keys()
        # Use ids to lookup products from db model
        products = Product.objects.filter(id__in=product_ids)
        # Get quantities directly from the cart dictionary
        quantities = self.cart
        # Start counting at 0
        total = 0

        for key, value in quantities.items():
            try:
                # Convert value to integer for multiplication
                quantity = int(value)
                key = int(key)
                
                for product in products:
                    if product.id == key:
                        if product.is_sale:
                            total = total + (product.sale_price * quantity)
                        else:
                            total = total + (product.price * quantity)
            except (ValueError, TypeError):
                # Handle cases where conversion fails
                continue
        
        return total


    
    def __len__(self):
        return len(self.cart)
    
    def get_prods(self):
        # Get product ids from cart
        product_ids = self.cart.keys()
        # Use ids to lookup products from db model
        products = Product.objects.filter(id__in=product_ids)

        return products
    
    def get_quants(self):
        quantities = self.cart
        return quantities
    
    def update(self, product, quantity):
        product_id = str(product)
        product_qty = str(quantity)

        # Get cart
        ourcart = self.cart

        # Update quantity
        ourcart[product_id] = product_qty

        self.session.modified = True

        

         # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.get(user__id=self.request.user.id)
            # Convert the cart to a string
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            # Save the cart to the user profile model
            current_user.old_cart = carty  # Directly assign the value
            current_user.save()  # Save the changes
            
        thing = self.cart
        return thing
    
    def delete(self, product):
        product_id = str(product)
        # Delete product from cart
        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True

         # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.get(user__id=self.request.user.id)
            # Convert the cart to a string
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            # Save the cart to the user profile model
            current_user.old_cart = carty  # Directly assign the value
            current_user.save()  # Save the changes