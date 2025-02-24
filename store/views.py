from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import SignUpForm, UpdateUserForm,ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django.db.models import Q
import json
from cart.cart import Cart

# Create your views here.

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def about(request):
    return render(request, 'about.html', {})

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            #  Do some shopping cart stuff here
            current_user = Profile.objects.get(user__id=request.user.id)

            # Get their saved cart from database
            saved_cart = current_user.old_cart
            # Convert database strings to python dictionary
            if saved_cart:
                # Convert string to dictionary using JSON 
                converted_cart = json.loads(saved_cart)
                # Add the loaded cart dictionary to our sessions
                # Get the cart
                cart = Cart(request)
                # Loop through the dictionary and add the items to the cart
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)


            messages.success(request, "Logged in successfully!")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials!")
    return render(request, 'login.html', {})

def logout_user(request):
   logout(request)
   messages.success(request, "Logged out successfully!")
   return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')

            # Login user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "User created successfully!")
            return redirect('update_info')
        else:
            messages.error(request, "An error occurred during registration.")
            return redirect('register')
    else:
        return render(request, 'register.html', {'form': form})
    

def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product': product})

def category(request, foo):
    foo = foo.replace('-', ' ')
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except:
        messages.error(request, "Category does not exist!")
        return redirect('home')
    
def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {'categories': categories})


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)


        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, "User updated successfully!")
            return redirect('home')
        return render(request, 'update_user.html', {'user_form': user_form})
    else:
        messages.error(request, "Please login to update your profile.")
        return redirect('login')
    

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form?
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # Is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, "Password updated successfully! Login with your new password.")
                # login(request, current_user)
                return redirect('login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
    else:
        messages.error(request, "Please login to update your password.")
        return redirect('home')
    
    return render(request, 'update_password.html', {'form': form})

def update_info(request):
    if request.user.is_authenticated:
        # Get the profile associated with the current user
        current_user_profile = Profile.objects.get(user__id=request.user.id)
        
        # Try to get the shipping address or create a new one if it doesn't exist
        try:
            shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        except ShippingAddress.DoesNotExist:
            shipping_user = ShippingAddress(user=request.user)
        
        # Get original User form
        form = UserInfoForm(request.POST or None, instance=current_user_profile)
        
        # Get User's Shipping form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        
        if form.is_valid() or shipping_form.is_valid():
            # Save original User form
            form.save()
            
            # Save Shipping form
            shipping_form.save()
            
            messages.success(request, "Information updated successfully!")
            return redirect('home')
        
        return render(request, 'update_info.html', {'form': form, 'shipping_form': shipping_form})
    else:
        messages.error(request, "Please login to update your information.")
        return redirect('login')
    

def search(request):
    # Determine if they filled out the form
    if request.method == 'POST':
        searched = request.POST['searched']
        # Query the products DB Model
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        # Test for null
        if not searched:
            messages.success(request, "No products found!")
            return render(request, 'search.html', {})
        else:
            return render(request, 'search.html', {'searched': searched}) 
    else:
        return render(request, 'search.html', {})