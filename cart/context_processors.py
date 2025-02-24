from .cart import Cart

# Create context processor to make cart available on all pages
def cart(request):
    return {'cart': Cart(request)}