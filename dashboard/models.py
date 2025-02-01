from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils import timezone
from .utils import generate_ref_code

from django.urls import reverse
from uuid import uuid4
from django_resized import ResizedImageField
from django.utils.translation import gettext as _
import os 
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings


import datetime
from datetime import timedelta
from datetime import datetime as dt


today = datetime.date.today()


from django_ckeditor_5.fields import CKEditor5Field


from django import forms

from django.db import models

class Hotel(models.Model):
    name = models.CharField(max_length=255)
    image_url = models.URLField()
    price_agoda = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_booking = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    star_rating = models.FloatField()
    agoda_url = models.URLField(null=True, blank=True)
    booking_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def best_price(self):
        """Returns the best price available"""
        prices = [p for p in [self.price_agoda, self.price_booking] if p is not None]
        return min(prices) if prices else None

    def __str__(self):
        return self.name

# Create your models here.
class Profile(models.Model):
        SUBSCRIPTION_OPTIONS = [
        ('free', 'free'),
        ('starter', 'starter'), 
        ('advanced', 'advanced'), 
        ]
        user = models.OneToOneField(User,on_delete=models.CASCADE)
        first_name = models.CharField(null=True, blank=True, max_length=100)
        last_name = models.CharField(null=True, blank=True, max_length=100)
        addressLine1 = models.CharField(null=True, blank=True, max_length=100)
        addressLine2 = models.CharField(null=True, blank=True, max_length=100)
        city = models.CharField(null=True, blank=True, max_length=100)
        province = models.CharField(null=True, blank=True, max_length=100)
        country = models.CharField(null=True, blank=True, max_length=100)
        postalCode = models.CharField(null=True, blank=True, max_length=100)
        profileImage = ResizedImageField(size=[200, 200], quality=90, upload_to='profile_images')
      
        monthlyCount = models.CharField( null=True, blank=True, max_length=100)
        subscribed = models.BooleanField(default=False)
        subscriptionType = models.CharField(choices=SUBSCRIPTION_OPTIONS,default='free', max_length=100)
        subscriptionReference = models.CharField( null=True, blank=True, max_length=100)
        bio = models.TextField(blank=True)
        code = models.CharField(max_length=12,blank=True)
        recommended_by = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True,related_name='reff_by')
        
       

        uniqueId = models.CharField(null=True, blank=True, max_length=100)
        slug = models.SlugField(max_length=250, unique=True, blank=True, null=True)
        date_created = models.DateTimeField(blank=True, null=True,auto_now=True)
        last_updated = models.DateTimeField(blank=True, null=True,auto_now_add=True)
        
      
	       

        def __str__(self):
            return  '{} {} {} '.format(self.user.first_name, self.user.last_name, self.user.email,self.code)
    

        def get__recommended_profiles(self):
            qs = Profile.objects.all()



        def save(self, *args, **kwargs):
            if self.date_created is None:
                self.date_created = timezone.localtime(timezone.now())
            if self.uniqueId is None:
                self.uniqueId = str(uuid4()).split('-')[4]
            if self.code =="":
                code = generate_ref_code() 
                self.code = code
            # self.slug = slugify('{} {} {} '.format(self.user.first_name, self.user.last_name, self.user.email))


            self.slug = slugify('{} {} {} '.format(self.user.first_name, self.user.last_name, self.user.email,self.code))
            self.last_updated = timezone.localtime(timezone.now())
            super(Profile, self).save(*args, **kwargs)
        

class Image(models.Model):
        phrase  =  models.CharField( max_length=200)
        ai_image  =  models.ImageField( upload_to = 'images')
        

        def __str__(self):
            return  str(self.phrase)


   