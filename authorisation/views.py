from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import redirect

def anonymous_required(function=None, redirect_url='dashboard'):
    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url
    )

    if function:
        return actual_decorator(function)
    return actual_decorator

@anonymous_required
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip().lower()
        password = request.POST.get('password')
        user = auth.authenticate(username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password. Please sign in.')
            return redirect('login')
    return render(request, 'authorisation/login.html')

@anonymous_required
def user_register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
      
        email = request.POST.get('email').strip().lower()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
          # Get the nationality value from the form


        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, f"A user with the email address '{email}' already exists. Please use a different email.")
            return redirect('register')

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
           
            email=email,
            username=email,
            password=password2,
            
        )
        auth_login(request, user)
        return redirect('dashboard')

    return render(request, 'authorisation/register.html')

@login_required(login_url='login')
def user_logout(request):
    auth_logout(request)
    return redirect('login')
