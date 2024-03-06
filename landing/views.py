from django.shortcuts import render, redirect, HttpResponse

# Create your views here.

def home(request):
    return render (request,'landing/index.html', {})

def pricing(request):
    return render (request,'landing/pricing.html', {})