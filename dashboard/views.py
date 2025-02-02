from django.shortcuts import render ,redirect,get_object_or_404
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect


from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from django.core.files.base import ContentFile
from dashboard.models import Image
from django.conf import settings
from django.views.generic.base import TemplateView

import datetime
from datetime import timedelta
from datetime import datetime as dt
import requests
import json



from .forms import *
from .models import *

import time 
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


import re



from django.core.mail import send_mail, BadHeaderError,EmailMessage



from django.forms.models import model_to_dict


from django.shortcuts import render


import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
import numpy as np
from django.shortcuts import render
from .models import Hotel

from .scrapy.agoda_scraper import save_agoda_hotels
from .scrapy.booking_scraper import save_booking_hotels



from .models import Hotel

from django.shortcuts import render, redirect, get_object_or_404
from .models import Hotel

from django.shortcuts import render
from .models import Hotel

from .forms import HotelSearchForm
from django.shortcuts import render
from .models import Hotel
from .scrapy import  agoda_scraper

def results(request):
    city_name = request.GET.get('city_name', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    star_rating = request.GET.get('star_rating')

    if not city_name:  # Prevent scraping with an empty city
        return render(request, 'dashboard/results.html', {'hotels': []})

    # Debugging Logs
    print(f"Scraping for: City={city_name}, Min={min_price}, Max={max_price}, Stars={star_rating}")

    # Call the Scrapy function to scrape data from Booking.com and Agoda
    hotels = agoda_scraper (city_name, min_price, max_price, star_rating)

    if not hotels:
        print("No hotels found during scraping.")

    return render(request, 'dashboard/results.html', {'hotels': hotels})


def bookmark_hotel(request, hotel_id):
    """Adds a hotel to the user's session-based bookmarks."""
    hotel = get_object_or_404(Hotel, id=hotel_id)
    bookmarks = request.session.get('bookmarks', [])

    if hotel.id not in bookmarks:
        bookmarks.append(hotel.id)

    request.session['bookmarks'] = bookmarks
    request.session.modified = True  # Ensure session is updated
    return redirect('dashboard')  # Redirect to the dashboard or search results page
def bookmarked_hotels(request):
    """Displays hotels bookmarked by the user."""
    bookmarks = request.session.get('bookmarks', [])
    hotels = Hotel.objects.filter(id__in=bookmarks)
    return render(request, 'dashboard/bookmarks.html', {'hotels': hotels})




def home(request):
    form = HotelSearchForm()
    return render(request, 'dashboard/home.html', {'form': form})


@login_required
def profile(request,*args, **kwargs):
    context = {}                      
                                  
    if request.method == 'GET':
        form  = ProfileForm(instance=request.user.profile,user=request.user)
        image_form =ProfileImageForm(instance=request.user.profile)
                                 
        context ['form'] =form                          
        context ['image_form'] =image_form
        return render(request, 'dashboard/profile.html', context)
    
    
    if request.method == 'POST':
        
        form = ProfileForm(request.POST ,instance=request.user.profile, user=request.user)
        image_form  = ProfileImageForm(request.POST,request.FILES,instance=request.user.profile)
       
        if form.is_valid():
           form.save()
           return redirect('profile') 
    
        if image_form.is_valid():
            image_form.save()
            return redirect('profile')
   
    return render(request, 'dashboard/profile.html', context)


