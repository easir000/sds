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

from PIL import Image

from .forms import *
from .models import *

import time 
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# importing the openai API
import openai
import re



from django.core.mail import send_mail, BadHeaderError,EmailMessage



from django.forms.models import model_to_dict


from django.shortcuts import render


import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from moviepy.editor import *
from moviepy.video.tools.segmenting import findObjects
import numpy as np
from django.shortcuts import render
from .models import Hotel
from .forms import SearchForm
from .scrapy.agoda_scraper import save_agoda_hotels
from .scrapy.booking_scraper import save_booking_hotels



def home(request):
    form = SearchForm(request.GET)
    hotels = Hotel.objects.all()

    if form.is_valid():
        city = form.cleaned_data.get("city_name")
        min_price = form.cleaned_data.get("min_price")
        max_price = form.cleaned_data.get("max_price")
        star_rating = form.cleaned_data.get("star_rating")

        # Trigger scraping
        agoda_url = f"https://www.agoda.com/city/{city.replace(' ', '-')}-my.html"
        booking_url = f"https://www.booking.com/searchresults.html?ss={city}"
        save_agoda_hotels(agoda_url)
        save_booking_hotels(booking_url)

        # Filter results
        if min_price:
            hotels = hotels.filter(price_agoda__gte=min_price) | hotels.filter(price_booking__gte=min_price)
        if max_price:
            hotels = hotels.filter(price_agoda__lte=max_price) | hotels.filter(price_booking__lte=max_price)
        if star_rating:
            hotels = hotels.filter(star_rating=star_rating)

    return render(request, "dashboard/home.html", {"form": form, "hotels": hotels})
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

######################################################### txt to image



######################################################### txt to image
@login_required
def generate_image_from_text(request):
    pass
    text_input = request.GET.get('text_input')
    image_url = None
    if text_input is not None:
        if '\n' in text_input:
            prompt = text_input
        else:
            features_input = request.GET.get('features_input')
            if features_input is not None:
                prompt = f"{text_input}\n{features_input}"
            else:
                prompt = text_input
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size='1024x1024',
        )
        image_url = response['data'][0]['url']
    context = {'image_url': image_url}
    return render(request, 'dashboard/images.html', context) 

######################################################### Human Like Content

