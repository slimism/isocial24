from django.shortcuts import render, redirect
from .models import Product, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm, ContactForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
import json
from cart.cart import Cart 
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Send the email
            send_mail(
                subject,
                f"Message from {name} ({email}):\n\n{message}",
                email,
                ['mysleeem@gmail.com'],  # Replace with your email address
                fail_silently=False,
            )

            messages.success(request, 'Your message has been sent. Thank you!')
            return redirect('home')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})



def home(request):
    products = Product.objects.all()
    return render (request, 'home.html', {'products': products})


def about(request):
    return render (request, 'about.html', {})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #Retrieve shopping cart 
            current_user = Profile.objects.get(user__id=request.user.id)
            #Get the saved cart from db 
            saved_cart = current_user.old_cart
            #Convert String to Dict 
            if saved_cart:
                #Convert to dict using json
                converted_cart = json.loads(saved_cart)
                #add loaded cart dict to our session 
                #get cart 
                cart = Cart(request)
                #Loop through the cart and add items from db 
                for key, value in converted_cart.items():
                    cart.db_add(product=key)


            messages.success(request, ("You've been logged in"))
            return redirect('home')
        else: 
            messages.success(request, ("There was an error, please try again"))
            return redirect('login')
    else:
        return render (request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out .. Thanks for stopping by"))
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            form.save()
            # Check if form is valid again before saving
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "User has been created. Please complete your profile.")
            # Redirect to profile update page or wherever needed after registration
            return redirect('update_info')
        else:
            # Use error message for form errors
            messages.error(request, "Oops! There was a problem registering. Please try again.")
            return redirect('register')
    else:
        return render(request, 'register.html', {'form': form})
    

def update_user(request):
    if request.user.is_authenticated:
        #Get current user
        current_user = User.objects.get(id=request.user.id)
        #Get Original User Form
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, "User has been updated!")
            return redirect('home')
        return render(request, "update_user.html", {'user_form': user_form})
    else:
        messages.success(request, "Please login to update the user.")
        return redirect('home')
    
def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        #Did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # is the form valid 
            if form.is_valid():
                form.save()
                messages.success(request, "Password has been updated")
                login(request, current_user)
                return redirect('home')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                return redirect('update_password')
                
        else:
            form = ChangePasswordForm(current_user)
            return render(request, "update_password.html", {'form': form})
    else:
        messages.success(request, "Please login to update the password.")
        return redirect('home')
    
    

def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        
        # Try to get the shipping info for the current user
        try:
            shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        except ShippingAddress.DoesNotExist:
            # If it doesn't exist, create a new ShippingAddress instance
            shipping_user = ShippingAddress(user=request.user)
            shipping_user.save()
        
        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        
        if form.is_valid() and shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request, "Profile Info has been updated!")
            return redirect('home')
        
        return render(request, "update_info.html", {'form': form, 'shipping_form': shipping_form})
    else:
        messages.success(request, "Please login to update the user.")
        return redirect('home')


    