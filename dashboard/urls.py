# from django.urls import path

from django.contrib import admin
from django.urls import include, path

from . import views
from .views import *
from django.conf import settings




urlpatterns = [
   
   
   
    
   path('images', views.generate_image_from_text, name='images'),
   path('home', views.home, name='dashboard'),
   path('profile', views.profile, name='profile'),
   path('<str:ref_code>/', views.profile, name='profile'),
   
   
]
   
   



