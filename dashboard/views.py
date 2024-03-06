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
from .functions import *
import time 
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# importing the openai API
import openai
import re

from .secret_key import API_KEY

# import stripe
# stripe.api_key = settings.STRIPE_SECRET_KEY

openai.api_key = API_KEY

OPENAI_API_KEY = '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'
openai.api_key = settings.OPENAI_API_KEYS

from django.core.mail import send_mail, BadHeaderError,EmailMessage
from .forms import ContactForm
from .models import ChatMessages


from django.forms.models import model_to_dict

from .forms import EditMessageForm
from django.shortcuts import render

from .models import GeneratedProductName

from .forms import RecipeForm
from .models import GeneratedRecipe


import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from moviepy.editor import *
from moviepy.video.tools.segmenting import findObjects
import numpy as np

from moviepy.editor import *

#########################################################
@login_required
def generate_video(request):
    # Define the screen size
    screensize = (820, 260)

    # Create a blank background
    background = ColorClip(screensize, color=(255, 255, 255), duration=5)  # Set the duration explicitly

    # Create a moving rectangle animation (same as before)
    def animate_rectangle(t):
        x = 50 + 200 * t  # Move the rectangle horizontally
        return ColorClip((100, 100), color=(255, 0, 0), duration=1).set_position((x, 'center'))

    # Create a text animation
    def animate_text(t):
        text = "Hello, World!"  # Text to display
        fontsize = 30  # Font size
        text_clip = TextClip(text, fontsize=fontsize, color='black')
        x = 100 + 100 * t  # Move the text horizontally
        return text_clip.set_position((x, 'center'))

    # Create a sequence of animated frames (concatenate the rectangle and text animations)
    animation_frames = [animate_rectangle(t).set_duration(1) for t in range(0, 5)] + [animate_text(t).set_duration(1) for t in range(0, 5)]

    # Create a video clip from the frames
    animation = concatenate_videoclips(animation_frames, method="compose", bg_color=(255, 255, 255))

    # Set the FPS of the final animation
    animation.fps = 24

    # ... Existing code for saving the animation ...

    # Return the URL to the saved animation
    animation_url = os.path.join(settings.MEDIA_URL, 'generated_animations', 'animation_example.mp4')
    context = {'animation_url': animation_url}
    return render(request, 'dashboard/generate_video.html', context)

@login_required
def Chat(request):
    try:
        if 'messages' not in request.session:
            request.session['messages'] = []

        if request.method == 'POST':
            prompt = request.POST.get('prompt')
            voice_text = request.POST.get('voiceText')  # Get voice text
            temperature = float(request.POST.get('temperature', 0.1))

            if prompt:
                user_message = ChatMessages(role='user', content=prompt, user=request.user)
                user_message.save()
                request.session['messages'].append(
                    model_to_dict(user_message, fields=['role', 'content', 'timestamp'])
                )

            if voice_text:
                voice_message = ChatMessages(role='user', content=voice_text, user=request.user)
                voice_message.save()
                request.session['messages'].append(
                    model_to_dict(voice_message, fields=['role', 'content', 'timestamp'])
                )

            assistant_message = ChatMessages(role='assistant', content="", user=request.user)
            assistant_message.save()

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=request.session['messages'][-10:],  # Include only the last 10 messages
                temperature=temperature,
                max_tokens=500,  # Adjust as needed
            )

            formatted_response = response['choices'][0]['message']['content']
            assistant_message.content = formatted_response
            assistant_message.save()

            request.session['messages'].append(
                model_to_dict(assistant_message, fields=['role', 'content', 'timestamp'])
            )
            request.session.modified = True

        messages = ChatMessages.objects.filter(user=request.user)
        context = {
            'messages': messages,
            'prompt': '',
            'temperature': 0.1,
        }
        return render(request, 'dashboard/chat.html', context)

    except Exception as e:
        print(e)
        return redirect('chat')


    
    
    
    
def new_chat(request):
    # clear the messages list
    request.session.pop('messages', None)
    return redirect('chat')


# this is the view for handling errors
# def error_handler(request):
#     # Your error handling logic here
#     return render(request, 'dashboard/error.html')
#     # return render(request, 'dashboard/chat.html')


   
def delete_message(request, message_id):
    # Get the ChatMessages instance to delete
    message = get_object_or_404(ChatMessages, id=message_id)

    # Check if the user is allowed to delete the message (you can add your own logic here)
    # For example, you might check if the user is the author of the message or has appropriate permissions

    # Delete the message
    message.delete()

    # Redirect back to the chat page or a suitable location
    return redirect('chat')  # Replace 'chat' with the actual URL name for your chat page



def edit_message(request, message_id):
    message = get_object_or_404(ChatMessages, id=message_id)

    # Check if the user is allowed to edit the message (add your own logic)

    if request.method == 'POST':
        form = EditMessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('chat')  # Replace 'chat' with the actual URL name for your chat page
    else:
        form = EditMessageForm(instance=message)

    context = {'form': form}
    return render(request, 'dashboard/edit_message.html', context)


def delete_full_history(request):
    # Delete all chat messages
    ChatMessages.objects.all().delete()

    # Redirect back to the chat page or a suitable location
    return redirect('chat') 




######################################################
def contactView(request):
    if request.method == "GET":
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            from_email = form.cleaned_data["from_email"]
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, from_email, ["easir956@gmail.com"])
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            return redirect("success")
    return render(request, "dashboard/email.html", {"form": form})

def successView(request):
    
    return HttpResponse("Success! Thank you for your message.")





@login_required
def lpg(request):
    context = {}
    if request.method =='POST':
        businessName = request.POST['businessName']
        businessDo = request.POST['businessDo']
        
        
        context ['section1Title'] = returnSection1Title(businessDo)
        context['section1Description'] = returnSection1Description(businessName,businessDo)
        
         
        #Get the service titles
        services = []
        serviceTitles =return3Services(businessDo)
        for service in serviceTitles:
            obj = {}
            serviceDescription = returnServiceDescription(service)
            obj['title'] = service 
            obj['description'] = serviceDescription
            services.append(obj)
            time.sleep (1)
            
        
        
        #Get the features titles
            
        features = []
        featureTitles = return3Features (businessDo)
        for feature in featureTitles:
            obj = {}
            featureDescription = returnFeatureDescription(features)
            obj['title'] = feature 
            obj['description'] = featureDescription
            features.append(obj) 
            time.sleep (1)
            
            
            
         
         
         
        context['service1Title']  = services [0]['title']
        context['service1Description'] = services [0]['description']
        context['service2Title']  = services [0]['title']
        context['service2Description'] = services [0]['description']
        context['service3Title'] = services [0]['title']
        context['service3Description'] = services [0]['description']
        
        
        context['section3Title'] = returnSection1Title(businessDo)
        context['section3Description'] = returnSection1Description(businessName,businessDo)
        
        context['features1Title'] = features[0]['title']
        context['features1Description'] = features[0]['description']
        context['features2Title'] = features[0]['title']
        context['features2Description'] = features[0]['description']
        context['features3Title'] = features[0]['title']
        context['features3Description'] = features[0]['description']
  
        
        return render (request,'dashboard/ai-website.html', context)
        
    return render (request,'dashboard/lpg.html', context)
    
@login_required
def website(request):
   context = {}
   
        
   return render (request,'dashboard/website.html', context)    
    
    
    
    
@login_required
def home(request):
    
    emptyBlogs = []
    completedBlogs= []
    monthCount = 0
    blogs=Blog.objects.filter(profile=request.user.profile)
    for blog in blogs:     
        sections = BlogSection.objects.filter(blog=blog)
        if sections.exists():
            blogWords = 0
            for section in sections:
              if section.wordCount:  
                blogWords += int(section.wordCount)
                monthCount = str(section.wordCount)
                
            blog.wordCount = str(blogWords)
            blog.monthlyCount = str(monthCount)
            blog.save()
            completedBlogs.append(blog)
        else:
            emptyBlogs.append(blog)
           
    context = {}
    context ['numBlogs'] = len(completedBlogs)
    context ['monthCount'] =request.user.profile.monthlyCount  
    context ['countReset'] =  '23rd-july ,2023 '                 
    context ['countReset'] =getNextSubscriptionDate(request.user.profile)
    context ['emptyBlogs'] =emptyBlogs     
    context ['completedBlogs'] =completedBlogs 
    context ['allowance'] = checkCountAllowance(request.user.profile) 
    
    
   

     
        
    return render (request,'dashboard/home.html', context)





def index(request):
	user_membership = UserMembership.objects.get(user=request.user)
	subscriptions = Subscription.objects.filter(user_membership=user_membership).exists()
	if subscriptions == False:
		return redirect('sub')
	else:
		subscription = Subscription.objects.filter(user_membership=user_membership).last()
		return render(request, 'dashboard/home.html', {'sub': subscription})





def subscription(request):
	return render(request, 'dashboard/subscription.html')

def end_sub(request):
	return render(request, 'sub.html')

def subscribe(request):
	plan = request.GET.get('sub_plan')
	fetch_membership = Membership.objects.filter(membership_type=plan).exists()
	if fetch_membership == False:
		return redirect('subscribe')
	membership = Membership.objects.get(membership_type=plan)
	price = float(membership.price)*100 # We need to multiply the price by 100 because Paystack receives in kobo and not naira.
	price = int(price)

	def init_payment(request):
		url = 'https://www.paypal.com/sdk/js?client-id=AUv8rrc_P-EbP2E0mpb49BV7rFt3Usr-vdUZO8VGOnjRehGHBXkSzchr37SYF2GNdQFYSp72jh5QUhzG&vault=true&intent=subscription'
		headers = {
			'Authorization': 'Bearer '+settings.PAYPAL_SECRET,
			'Content-Type' : 'application/json',
			'Accept': 'application/json',
			}
		datum = {
			"email": request.user.email,
			"amount": price
			}
		x = requests.post(url, data=json.dumps(datum), headers=headers)
		if x.status_code != 200:
			return str(x.status_code)
		
		results = x.json()
		return results
	initialized = init_payment(request)
	print(initialized['data']['authorization_url'])
	amount = price/100
	instance = PayHistory.objects.create(amount=amount, payment_for=membership, user=request.user, paystack_charge_id=initialized['data']['reference'], paystack_access_code=initialized['data']['access_code'])
	UserMembership.objects.filter(user=instance.user).update(reference_code=initialized['data']['reference'])
	link = initialized['data']['authorization_url']
	return HttpResponseRedirect(link)
# return render(request, 'dashboard/subscribe.html')

def call_back_url(request):
	reference = request.GET.get('reference')
	# We need to fetch the reference from PAYMENT
	check_pay = PayHistory.objects.filter(paystack_charge_id=reference).exists()
	if check_pay == False:
		# This means payment was not made error should be thrown here...
		print("Error")
	else:
		payment = PayHistory.objects.get(paystack_charge_id=reference)
		# We need to fetch this to verify if the payment was successful.
		def verify_payment(request):
			url = 'https://www.paypal.com/sdk/js?client-id=AUv8rrc_P-EbP2E0mpb49BV7rFt3Usr-vdUZO8VGOnjRehGHBXkSzchr37SYF2GNdQFYSp72jh5QUhzG&vault=true&intent=subscription'+reference
			headers = {
				'Authorization': 'Bearer '+settings.PPAYPAL_SECRET,
				'Content-Type' : 'application/json',
				'Accept': 'application/json',
				}
			datum = {
				"reference": payment.paystack_charge_id
				}
			x = requests.get(url, data=json.dumps(datum), headers=headers)
			if x.status_code != 200:
				return str(x.status_code)
			
			results = x.json()
			return results
	initialized = verify_payment(request)
	if initialized['data']['status'] == 'success':
		PayHistory.objects.filter(paystack_charge_id=initialized['data']['reference']).update(paid=True)
		new_payment = PayHistory.objects.get(paystack_charge_id=initialized['data']['reference'])
		instance = Membership.objects.get(id=new_payment.payment_for.id)
		sub = UserMembership.objects.filter(reference_code=initialized['data']['reference']).update(membership=instance)
		user_membership = UserMembership.objects.get(reference_code=initialized['data']['reference'])
		Subscription.objects.create(user_membership=user_membership, expires_in=dt.now().date() + timedelta(days=user_membership.membership.duration))
		return redirect('subscribed')
	return render(request, 'dashboard/payment.html')


def subscribed(request):
	return render(request, 'dashboard/subscribed.html')



 
# @login_required(login_url='login')
# def profile(request):
#     context = {}  
#     if request.method == "POST":
#         form = ProfileForm(request.POST , request.FILES, instance=request.user.profile, user=request.user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, ('Your profile was successfully created!!'))
#         else:
#             messages.error(request, 'Error saving form')

#         return redirect("profile")
    
#     # else:
#     #     user = request.user
#     #     profile = user.profile
#     #     form = ProfileForm(instance=profile)

#     # context = {'form' : form}
#     return render(request , 'dashboard/profile.html' , context)








# ###################################################################################



#########                 ######                #####            #####

######################################################### Profile

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

# @login_required
# def generate_image_from_text(request):
#     context={} 
#     object = None
#     if settings.OPENAI_API_KEYS is not None and request.method == 'POST':
        
#         web = request.POST.get('web')
        
#         # Call the OpenAI API to translate the input
        
#         response = openai.Image.create(
            
#             prompt= web,
#             n=1,
#             size = '256x256' # 512x512 1024x1024
#             )
#         print(response)
#         img_url = response["data"][0]["url"]
#         response = requests.get(img_url)
#         img_file = ContentFile(response.content)
#         count = Image.objects.count() +1
#         fname = f"image-{count}.jpg"
#         object = Image(phrase = web)
#         object.ai_image.save (fname, img_file)
#         object.save()
#         print(object)
        
        
#     return render(request, 'dashboard/images.html', context) 



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

@login_required
def content_generator(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        # prompt="Imagine you are a content generator. To write effective content both perplexity and burstiness are important. Perplexity assesses text complexity and burstiness evaluates sentence variation. People often write with a mix of long and short sentences, while machine generated sentences tend to be uniform. I will provide you with an (article) and ask you to rewrite it when composing the content you need to ensure a suitable balance of both perplexity and burstiness."
        prompt = request.POST['prompt']
        if prompt == "More Persuasive":
            prompt = "Rewrite my text with powerful, convincing language that will leave my readers no choice but to take action."
        elif prompt == "More Informative":
            prompt = "Rewrite my text with rich, informative details that will leave my readers feeling educated and informed."
        elif prompt == "More Descriptive":
            prompt = "Rewrite my text with evocative, descriptive language that paints a vivid and unforgettable picture in my readers’ minds."
        elif prompt == "More Humorous":
            prompt = "Rewrite my text with clever, comedic touches that will leave my readers laughing and entertained."
        elif prompt == "Urgent":
            prompt = "Rewrite my text with urgent, action-oriented language that will inspire my readers to take immediate action."
        elif prompt == "More Emphatic":
            prompt = "Rewrite my text with emphasis on the emotions and feelings of the characters or subjects I’m writing about, making the reader feel and connect with the story more."
        elif prompt == "More Concise":
            prompt = "Rewrite my text using more concise and to-the-point language, making it more direct and easy to understand for my readers."

        # Call the OpenAI API to generate content
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            temperature=0.7,
            max_tokens=2560,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Extract the generates from the response
        generates = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/contentgeneratorresults.html', {'generates': generates})

    # Render the content generator form template
    return render(request, 'dashboard/content_generator.html')


#########                 ######                #####            #####  Chat
#########################################################
@login_required
def Q_A(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/qaresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/qa.html')

#########################################################

@login_required
def Interview_Questions(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/iqresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/iq.html')


######################################################

@login_required
def Marv_Sarcastic_Chat_Bot(request):
    if request.method == 'POST':
        # Get the user input from the form
        # prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": "You are Marv, a chatbot that reluctantly answers questions with sarcastic responses."
            },
            {
            "role": "user",
            "content": "How many pounds are in a kilogram?"
            },
            {
            "role": "assistant",
            "content": "This again? There are 2.2 pounds in a kilogram. Please make a note of this."
            },
            {
            "role": "user",
            "content": "What does HTML stand for?"
            },
            {
            "role": "assistant",
            "content": "Was Google too busy? Hypertext Markup Language. The T is for try to ask better questions in the future."
            },
            {
            "role": "user",
            "content": "When did the first airplane fly?"
            },
            {
            "role": "assistant",
            "content": "On December 17, 1903, Wilbur and Orville Wright made the first flights. I wish they’d come and take me away."
            },
            {
            "role": "user",
            "content": "What time is it?"
            }
        ],
        temperature=0.5,
        max_tokens=2560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )

        # Extract the translations from the response
        translations = response['choices'][0]['message']['content'].split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/mscbresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/mscb.html')
    


#########                 ######                #####            #####  Code


#########################################################

@login_required
def ML_AI_Language_Model_Tutor(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/mlairesults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/mlai.html')

#########################################################

@login_required
def NL_TO_API(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/results.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/NL to ChalkrAI API.html')


#########################################################

@login_required
def NL_TO_SAPI(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/striperesults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/NL to Stripe API.html')

#########################################################

@login_required
def SQL_Request(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/srresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/sr.html')

#########################################################


@login_required
def PL_To_NL(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/nresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/Python to natural language.html')


#########################################################

@login_required
def C_T_C(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/Complexity.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/ctc.html')

#########################################################

@login_required
def T_P_L(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/tplresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/tpl.html')

#########################################################


@login_required
def E_C(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/ecresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/ec.html')


#########################################################


@login_required
def P_B_F(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']
#         prompt = """Please fix the bug in the following Python code:

# def calculate_average(numbers):
#     total = 0
#     for number in numbers:
#         total += number
#     average = total / len(numbers)
#     return average

# numbers = [5, 10, 15, 20]
# result = calculate_average(numbers)
# print(result)
# """,

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/pbfresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/pbf.html')

#########################################################


@login_required
def J_H_C(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/pbfresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/jhc.html')

#########################################################


@login_required
def J_T_P(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/jtpresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/jtp.html')

#########################################################


@login_required
def W_P_D(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/wpdresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/wpd.html')

#########################################################


@login_required
def J_O_L_F(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/jolfresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/jolf.html')




#########                 ######                #####            #####  Academic
#########################################################

@login_required
def C_T_C(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/Complexity.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/ctc.html')

#########################################################


@login_required
def G_C(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/gcresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/gc.html')

#########################################################


@login_required
def Summarize(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/sf2gresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/sf2g.html')

#########################################################


@login_required
def E_Translate(request):
    if request.method == "POST":
        source_text = request.POST.get("source_text")
        target_language = request.POST.get("target_language")

        # Replace 'YOUR_OPENAI_API_KEY' with your actual API key
        openai.api_key = "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"

        # Construct a prompt with the target language as part of the text
        prompt = f"Translate the following text to {target_language}:\n{source_text}"

        # Call the OpenAI API with the appropriate language model
        response = openai.Completion.create(
            engine="text-davinci-002",  # Use the language model of your choice
            prompt=prompt,
            max_tokens=200,
            stop=None,
            temperature=0.7,
        )


        # Extract the translated text from the response
        translations = response.choices[0].text.split('\n')
        
        return render(request, "dashboard/etolresults.html", { "translations": translations})
            
    else:
        return render(request, "dashboard/etol.html")
        
        
       

#########################################################


@login_required
def Parse_unstructured_data(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/pudresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/pud.html')
#########################################################

@login_required
def TL_DR_Summarization(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/tldrresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/tldr.html')
#########################################################

@login_required
def Spreadsheet_Creator(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/scrresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/sc.html')



#########################################################

@login_required
def Analogy_Maker(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/amresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/am.html')


#########################################################

@login_required
def Third_Person_Converter(request):
    if request.method == "POST":
        source_text  = request.POST.get("source_text")
        converted_text = request.POST.get("converted_text")
        
       

        # Replace 'YOUR_OPENAI_API_KEY' with your actual API key
        openai.api_key = "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"

        # Construct a prompt with the target language as part of the text
        prompt = f"Convert the following first-person text to 6 examples of  2nd and ThirdPerson Convert:{converted_text}:\n{source_text}"
       

        # Call the OpenAI API with the appropriate language model
        response = openai.Completion.create(
            engine="text-davinci-002",  # Use the language model of your choice
            prompt=prompt,
            max_tokens=2560,
            stop=None,
            temperature=0.7,
        )

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/tpcresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/tpc.html')

#########################################################

@login_required
def Notes_To_Summary(request):
    if request.method == "POST":
        source_text = request.POST.get("source_text")
        essay_topic = request.POST.get("essay_topic")
        
        target_language = request.POST.get("target_language")

        # Replace 'YOUR_OPENAI_API_KEY' with your actual API key
        openai.api_key = "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"

        # Construct a prompt with the target language as part of the text
        prompt = f"Convert  the following Notes to summary in 6 strong meaningful Lines {target_language}:\n{source_text}"

        # Call the OpenAI API with the appropriate language model
        response = openai.Completion.create(
            engine="text-davinci-002",  # Use the language model of your choice
            prompt=prompt,
            max_tokens=200,
            stop=None,
            temperature=0.7,
        )

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/ntcresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/ntc.html')

#########################################################

@login_required
def Essay_Outline(request):
    if request.method == 'POST':
        # Get the user input from the form
        essay_topic = request.POST['essay_topic'][:60]
        essay_type = request.POST['essay_type'][:60]
        essay_purpose = request.POST['essay_purpose'][:160]
        desired_essay_length = request.POST['desired_essay_length'][:60]
        academic_level = request.POST['academic_level'][:60]
        specific_instructions = request.POST['specific_instructions'][:60]

        # Construct the prompt based on the user inputs
        prompt = (
            f"Essay Topic: {essay_topic}\n"
            f"Essay Type: {essay_type}\n"
            f"Essay Purpose: {essay_purpose}\n"
            f"Desired Essay Length: {desired_essay_length}\n"
            f"Academic Level: {academic_level}\n"
            f"Specific Instructions: {specific_instructions}\n"
        )

        try:
            # Replace 'YOUR_OPENAI_API_KEY' with your actual API key
            openai.api_key = "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"

            # Call the OpenAI API to generate the essay outline
            response = openai.Completion.create(
                model="gpt-3.5-turbo",
                prompt=prompt,
                temperature=0.7,
                max_tokens=560,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            # Extract the generated essay outline from the response
            essay_outline = response.choices[0].text.split('\n')
            
            max_length = 60  # Convert desired length to integer
            if len(essay_outline) > max_length:
                essay_outline = essay_outline[:max_length]

            # Render the result in the 'essay_outline.html' template
            return render(request, 'dashboard/eoresults.html', {'essay_outline': essay_outline})

        except Exception as e:
            # Handle any errors that might occur during the API call
            return render(request, 'dashboard/error.html', {'error_message': str(e)})
    
    return render(request, 'dashboard/eo.html')  # Display the form initially

        


#########################################################

@login_required
@csrf_exempt
def Create_Study_Notes(request):
    if request.method == 'POST':
        try:
            # Get user input from the form
            note_topic = request.POST.get('note_topic', '')[:60]  # Limit to 60 characters
            note_type = request.POST.get('note_type', 'general')  # Default to general notes
            note_length = request.POST.get('note_length', '500')  # Default to 500 words
            language_style = request.POST.get('language_style', 'neutral')  # Default to neutral
            key_concepts = request.POST.get('key_concepts', '')  # Default to empty
            additional_instructions = request.POST.get('additional_instructions', '')  # Default to empty
            study_level = request.POST.get('study_level', 'intermediate')  # Default to intermediate
            citation_format = request.POST.get('citation_format', 'APA')  # Default to APA
            include_examples = request.POST.get('include_examples', 'yes')  # Default to yes
            visual_aids = request.POST.get('visual_aids', 'no')  # Default to no
            text_formatting = request.POST.get('text_formatting', 'plain')  # Default to plain text
            content_organization = request.POST.get('content_organization', '')  # Default to empty

            # Construct the prompt based on the user inputs
            prompt = (
                f"Generate {note_type} study notes on the topic: {note_topic}\n"
                f"Note Type: {note_type}\n"
                f"Note Length: {note_length} words\n"
                f"Preferred Language Style: {language_style}\n"
                f"Key Concepts to Include: {key_concepts}\n"
                f"Additional Instructions: {additional_instructions}\n"
                f"Study Level: {study_level}\n"
                f"Citation Format: {citation_format}\n"
                f"Include Examples: {include_examples}\n"
                f"Visual Aids: {visual_aids}\n"
                f"Text Formatting: {text_formatting}\n"
                f"Content Organization: {content_organization}\n"
            )

            # Set OpenAI API key
            openai.api_key = "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"

            # Call the OpenAI API to generate the study note
            response = openai.Completion.create(
                engine="gpt-3.5-turbo",
                prompt=prompt,
                max_tokens=2560,
                top_p=0.8,
                temperature=0.7
            )

            # Extract the generated study note from the response
            study_note = response.choices[0].text.strip()
            
            # Apply text formatting based on the selected option
            if text_formatting == 'bold':
                study_note = f"<strong>{study_note}</strong>"
            elif text_formatting == 'italic':
                study_note = f"<em>{study_note}</em>"

            
            study_note_obj = StudyNote(
                note_topic=note_topic,
                note_type=note_type,
                note_length=note_length,
                language_style=language_style,
                key_concepts=key_concepts,
                additional_instructions=additional_instructions,
                study_level=study_level,
                citation_format=citation_format,
                include_examples=include_examples,
                visual_aids=visual_aids,
                text_formatting=text_formatting,
                content_organization=content_organization,
                generated_note=study_note
            )
            study_note_obj.save()
            # Render the result in a template (e.g., 'csnresults.html')
            return render(request, 'dashboard/csnresults.html', {
                'study_note': study_note,
                'note_type': note_type,
                'note_length': note_length,
                'language_style': language_style,
                'key_concepts': key_concepts,
                'additional_instructions': additional_instructions,
                'study_level': study_level,
                'citation_format': citation_format,
                'include_examples': include_examples,
                'visual_aids': visual_aids,
                'text_formatting': text_formatting,
                'content_organization': content_organization
            })

        except Exception as e:
            # Handle any errors that might occur during the API call
            return render(request, 'error.html', {'error_message': str(e)})

    return render(request, 'dashboard/csn.html')  # Display the form initially

######   ###################   ################  Digital marketting

#########################################################



@login_required
def Ad_From_Product_Description(request):
    if request.method == 'POST':
        # Get the user input from the form
        product_name = request.POST['product_name']
        product_description = request.POST['product_description']
        unique_feature = request.POST['unique_feature']
        audience = request.POST['audience']
        tone_of_voice = request.POST['tone_of_voice']  # Added this line
        language = request.POST['target_language']
        keywords = request.POST['keywords']
        # domain = request.POST['domain']
        intent = request.POST['intent']

        domain = request.POST['domain']
        if not is_valid_domain(domain):
            return render(request, 'dashboard/afpd.html', {'error': 'Invalid domain format'})

        # Create a prompt combining all the inputs
        prompt = f"Product: {product_name}\nDescription: {product_description}\nUnique Feature: {unique_feature}\nTone of Voice: {tone_of_voice}\nDomain: {domain}\n\nCreate a compelling advertisement for this product:"

        # Call the OpenAI API to generate the advertisement
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            temperature=0.7,
            max_tokens=500,  # Adjust as needed
            top_p=1,
            frequency_penalty=0.2,
            presence_penalty=0.5
        )

         
        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/afpdresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/afpd.html')
def is_valid_domain(domain):
    pattern = r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$"
    return re.match(pattern, domain.lower()) is not None

#########################################################


def Product_Name_Generator(request):
    selected_keyword = request.POST.get('selected_keyword', '')
    custom_keyword = request.POST.get('custom_keyword', '')
    generated_name = None
    error_message = None
    product_names = None

    if selected_keyword:
        keyword_to_use = selected_keyword
    elif custom_keyword:
        keyword_to_use = custom_keyword
    else:
        error_message = "Please select or enter a keyword."

    if 'keyword_to_use' in locals():
        try:
            user = request.user
            openai.api_key = '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'
            prompt = f"Generate product names based on the keyword: {keyword_to_use}"
            response = openai.Completion.create(
                engine="gpt-3.5-turbo",
                prompt=prompt,
                max_tokens=50  # Adjust as needed
            )
            generated_name = response.choices[0].text.strip()

            # Save the generated name to the database
            
            GeneratedProductName.objects.create(user=user, example_words=keyword_to_use, generated_name=generated_name)
            # Fetch all previously generated product names
            
            product_names = GeneratedProductName.objects.filter(user=user)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"

    return render(request, 'dashboard/png.html', {'generated_name': generated_name, 'error_message': error_message, 'product_names': product_names})
# def index(request):
#     return render(request, 'dashboard/png.html')


#########################################################


@login_required
def Extract_Contact_Information(request):
    if request.method == 'POST':
        # Get the user input from the form
        input_text = request.POST['input_text']

        # Define the prompt
        prompt = f"Extract any contact information from the following text:\n{input_text}\nExtracted information:"

        # Call the OpenAI API to extract contact information
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            temperature=0.4,  # Adjust temperature as needed
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Extracted information from the response
        extracted_info = response.choices[0].text.strip()
        # You can implement your own post-processing logic here to extract relevant contact information
        extracted_contacts = extract_contacts(extracted_info)  # Implement this function

        # Render the results template with the extracted information
        return render(request, 'dashboard/eciresults.html', {'extracted_contacts': extracted_contacts, 'input_text': input_text})

    # Render the contact extraction form template
    return render(request, 'dashboard/eci.html')


def extract_contacts(text):
    # Define a regular expression pattern for matching email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    
    # Find all email addresses in the text using the pattern
    extracted_emails = re.findall(email_pattern, text)
    
    return extracted_emails

#########################################################

@login_required
def Recipe_Creator(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe_title = form.cleaned_data['recipe_title']
            recipe_text = form.cleaned_data['recipe_text']

            # Provide image URLs in the prompt
            prompt = f"## Recipe: {recipe_title}\n\n" \
                     f"### Description:\n{recipe_text}\n\n" \
                     f"### Ingredients:\n- Ingredient 1\n- Ingredient 2\n- Ingredient 3\n\n" \
                     f"### Instructions:\n1. Step 1\n2. Step 2\n3. Step 3\n\n" \
                     f"![Image description](image_url_here)"

            response = openai.Completion.create(
                engine="gpt-3.5-turbo",  # Use the appropriate engine name
                prompt=prompt,
                max_tokens=1300,  # Adjust as needed
            )

            generated_recipe_text = response.choices[0].text.strip()

            # Save the generated recipe to the database
            generated_recipe = GeneratedRecipe.objects.create(
                title=recipe_title,
                text=recipe_text,
                generated_text=generated_recipe_text,
            )

            return render(
                request,
                'dashboard/rcresults.html',
                {'generated_recipe': generated_recipe},
            )
    else:
        form = RecipeForm()

    return render(request, 'dashboard/rc.html', {'form': form})




# @login_required
# def Recipe_Creator(request):
#     if request.method == 'POST':
#         # Get the user input from the form
#         recipe_title = request.POST['recipe_title']
#         recipe_text = request.POST['recipe_text']

#         # Create a prompt combining the title and text
#         prompt = f"## {recipe_title}\n{recipe_text}\nImage:"

#         # Call the OpenAI API to generate a recipe
#         response = openai.Completion.create(
#             model="gpt-3.5-turbo",
#             prompt=prompt,
#             temperature=0.7,
#             max_tokens=1560,
#             top_p=1,
#             frequency_penalty=0,
#             presence_penalty=0
#         )

#         # Extract the generated recipe from the response
#         generated_recipe = response.choices[0].text.strip()

#         # Render the results template with the generated recipe
#         return render(request, 'dashboard/rcresults.html', {'generated_recipe': generated_recipe})

#     # Render the recipe creation form template
#     return render(request, 'dashboard/rc.html')


#########################################################

@login_required
def Restaurant_Review_Creator(request):
    tones = [
        {'id': 1, 'value': 'Casual', 'label': 'Casual'},
        {'id': 2, 'value': 'Convincing', 'label': 'Convincing'},
        {'id': 3, 'value': 'Critical', 'label': 'Critical'},
        {'id': 4, 'value': 'Formal', 'label': 'Formal'},
        {'id': 5, 'value': 'Funny', 'label': 'Funny'},
        {'id': 6, 'value': 'Humble', 'label': 'Humble'},
        {'id': 7, 'value': 'Humorous', 'label': 'Humorous'},
        {'id': 8, 'value': 'Informative', 'label': 'Informative'},
        {'id': 9, 'value': 'Inspirational', 'label': 'Inspirational'},
        {'id': 10, 'value': 'Joyful', 'label': 'Joyful'},
        {'id': 11, 'value': 'Passionate', 'label': 'Passionate'},
        {'id': 12, 'value': 'Thoughtful', 'label': 'Thoughtful'},
        {'id': 13, 'value': 'Urgent', 'label': 'Urgent'},
        {'id': 14, 'value': 'Worried', 'label': 'Worried'},
    ]
    
    if request.method == 'POST':
        restaurant_name = request.POST.get('restaurant_name')
        highlights = request.POST.get('highlights')
        selected_tone = request.POST.get('tone')  # Get the selected tone from the form
        
        # Make a request to OpenAI API to generate review
        openai_api_key = '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'
        openai_endpoint = 'https://api.openai.com/v1/engines/davinci-codex/completions'
        prompt = f"Restaurant: {restaurant_name}\nHighlights: {highlights}\nTone: {selected_tone}\nReview:"
        
        response = requests.post(openai_endpoint, json={
            'prompt': prompt,
            'max_tokens': 150,  # Adjust as needed
        }, headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {openai_api_key}',
        })
        
        generated_review = response.json()['choices'][0]['text']
        
        return render(request, 'dashboard/rrc.html', {'tones': tones, 'generated_review': generated_review})
    
    return render(request, 'dashboard/rrc.html', {'tones': tones})

    #     # Extract the translations from the response
    #     translations = response.choices[0].text.split('\n')

    #     # Render the results template with the translations
    #     return render(request, 'dashboard/rrcresults.html', {'translations': translations})

    # # Render the translation form template
    # return render(request, 'dashboard/rrc.html')


#########################################################

@login_required
def VR_Fitness_Idea_Generator(request):
    if request.method == 'POST':
        # Get the user input from the form
        prompt = request.POST['prompt']

        # Call the OpenAI API to translate the input
        response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=560,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        # Extract the translations from the response
        translations = response.choices[0].text.split('\n')

        # Render the results template with the translations
        return render(request, 'dashboard/vfigresults.html', {'translations': translations})

    # Render the translation form template
    return render(request, 'dashboard/vfig.html')


############# ################## ################ web content


@login_required
def blogTopic(request):
  context={}
  if request.method == 'POST':
      #retriving the blogIdea String from thr submitted Form which comes in the request.POST

    blogIdea = request.POST['blogIdea']
    #SAVING THAT blogIdea in the session to access later in another route for example
    request.session['blogIdea']=blogIdea
    keywords = request.POST['keywords']
    request.session['keywords']=keywords
    audience = request.POST['audience']
    request.session['audience']=audience


    blogTopics = generateBlogTopicIdeas (blogIdea,audience,keywords)
    if len(blogTopics)>0:
        request.session['blogTopics'] = blogTopics
        return redirect('blog-sections')
    else:
    
        messages.error(request, 'Sorry We could not able to generate any idea for you , please try again')
        return redirect('blog-topic')

    
  return render(request, 'dashboard/blog-topic.html', context)  

@login_required
def blogSections(request):
    
    if 'blogTopics' in request.session:
        pass
            
    else:
            messages.error(request, "start by creating blog topic Ideas")
            return redirect('blog-topic')
    context={} 
    context['blogTopics'] =  request.session['blogTopics']
    return render(request, 'dashboard/blog-sections.html', context) 


@login_required  
def deleteBlogTopic (request,uniqueId):
    try: 
        blog= Blog.objects.get(uniqueId= uniqueId)
        if blog.profile == request.user.profile:
            blog.delete()
            return redirect ('dashboard')
        else:
            messages.error(request, "Access denied")
            return redirect ('dashboard')
    except:
            messages.error(request, "Blog not found this time , Please try again later")
            return redirect ('dashboard')
        
@login_required
def saveBlogTopic(request,blogTopic):
    if 'blogIdea' in request.session and 'keywords' in request.session and'audience' in request.session and 'blogTopics'  in request.session:
    
            blog=Blog.objects.create(
            title  = blogTopic,
            blogIdea  = request.session['blogIdea'],
            keywords= request.session['keywords'],
            audience= request.session['audience'],
            profile = request.user.profile)
            blog.save()
            blogTopics =  request.session['blogTopics']
            blogTopics.remove(blogTopic)
            request.session['blogTopics'] = blogTopics
            return redirect('blog-sections')
            
    else:
            return redirect('blog-topic')

 
       
@login_required   
def useBlogTopic(request,blogTopic):
    context = {}
    if 'blogIdea' in request.session and 'keywords' in request.session and'audience' in request.session :
       
       if Blog.objects.filter(title =blogTopic).exists():
           blog = Blog.objects.get(title =blogTopic)
       else: 
           #start by saving blog ...
            blog=Blog.objects.create(
            title  = blogTopic,
            blogIdea  = request.session['blogIdea'],
            keywords= request.session['keywords'],  
            audience= request.session['audience'],
            profile = request.user.profile)
            blog.save()
       blogSections = generateBlogSectionTitles(blogTopic,request.session['audience'],request.session['keywords'])
        
    else:
        return redirect('blog-topic')
    if request.method == 'POST':
        for val in request.POST:
            if not 'csrfmiddlewaretoken' in val :
                prevBlog= ''
                bSections = BlogSection.objects.filter(blog=blog).order_by('date_created')
                for sec in bSections:
                    prevBlog += sec.title + '\n'
                    prevBlog += sec.body.replace('<br>','\n')
                prevBlog = ''   
                section = generateBlogSectionDetails(blogTopic,val, request.session['audience'] ,request.session ['keywords'] ,prevBlog,request.user.profile)
                # Create database record
                blogSec = BlogSection.objects.create(
                title= val,
                body = section,
                blog =blog)
                blogSec.save()
                time.sleep(2)
        return redirect ('view-generated-blog', slug=blog.slug)
    
    
            
            
            
    if len (blogSections)>0:
        #adding the sections to the session
        request.session ['blogSections'] = blogSections
        #adding the sections to the context
        
        context ['blogSections'] = blogSections
        # context ['slug'] = blog.slug
        
        # return redirect ('select-blog-sections')
    else: 
        messages.error(request, "not possible from AI system , Please try again later")
        return redirect ('blog-topic')
    
    
    
        
    return render (request , 'dashboard/select-blog-sections.html', context)



           
@login_required   
def createBlogFromTopic(request,uniqueId):
    context = {}
    try:
        blog = Blog.object.get(uniqueId= uniqueId)
    except:
        messages.error(request, "Blog not found")
        return redirect ('dashboard')
    
    blogSections = generateBlogSectionTitles(blog.title,blog.audience,blog.keywords)
    
    if len (blogSections)>0:
        #adding the sections to the session
        request.session ['blogSections'] = blogSections
        #adding the sections to the context
        
        context ['blogSections'] = blogSections
        # context ['slug'] = blog.slug
        
        # return redirect ('select-blog-sections')
    else: 
        messages.error(request, "not possible from AI system , Please try again later")
        return redirect ('blog-topic')
    
    
    if request.method == 'POST':
        for val in request.POST:
            if not 'csrfmiddlewaretoken' in val :
                prevBlog= ''
                bSections = BlogSection.objects.filter(blog= blog).order_by('date_created')
                for sec in bSections:
                    prevBlog = sec.title + '\n'
                    prevBlog += sec.body.replace('<br>','\n')
                prevBlog = ''
                section = generateBlogSectionDetails(blog.title,val,blog.audience,blog.keywords,prevBlog,request.user.profile)
                # Create database record
                blogSec = BlogSection.objects.create(
                title= val,
                body = section,
                blog =blog)    
                blogSec.save()
                time.sleep(2)
            bSections = BlogSection.objects.filter(blog= blog)
            context = {}
            context ['blog'] = blog
            context ['blogSections'] = blogSections
        
            return redirect ('view-generated-blog', slug=blog.slug)
        
        return render (request , 'dashboard/select-blog-sections.html', context)


        
@login_required   
def rewriteBlog(request,uniqueId):
    
    try:
        blog = Blog.object.get(uniqueId= uniqueId)
    except:
        messages.error(request, "Blog not found")
        return redirect ('dashboard')
    
    titles = []
    blogSections = BlogSection.objects.filter(blog= blog).order_by('date_created')
    for section in blogSections:
        titles.append(section.title)
        section.delete()
    for val in titles:
        prevBlog= ''
        bSections = BlogSection.objects.filter(blog= blog).order_by('date_created')
        for sec in bSections:
            prevBlog = sec.title + '\n'
            prevBlog += sec.body.replace('<br>','\n')
        prevBlog = ''
        section = generateBlogSectionDetails(blog.title,val,blog.audience,blog.keywords,prevBlog,request.user.profile)
        # Create database record
        blogSec = BlogSection.objects.create(
        title= val,
        body = section,
        blog =blog)    
        blogSec.save()
        time.sleep(5)
        
    bSections = BlogSection.objects.filter(blog= blog)
    context = {}
    context ['blog'] = blog
    context ['blogSections'] = blogSections
    
        # return redirect ('view-generated-blog', slug=blog.slug)
        
    return render (request , 'dashboard/view-generated-blog.html', context)



@login_required  
def viewGeneratedBlog(request, slug):
    try:
        blog = Blog.objects.get(slug=slug)
    except:
        
        messages.error(request, " Please try again later")
        return redirect ('blog-topic')
    # fetch the created section for the blog
    blogSections = BlogSection.objects.filter(blog= blog)
    context = {}
    context ['blog'] = blog
    context ['blogSections'] = blogSections
    
    return render (request , 'dashboard/view-generated-blog.html', context)
    
  
  
 
@login_required  
def billing(request):
    context = {}  
    return render (request , 'dashboard/billing.html', context)
  
@require_POST 
@csrf_exempt
def webhook(request):
     return redirect ('billing')  
        
@login_required
def PaypalPaymentSuccess(request):
    if request.POST['type'] == 'starter':
        try:
            profile = Profile.objects.get(uniqueID = request.POST['userId'])
            profile.subscribed= True
            profile.subscriptionType= 'Starter'
            profile.subscriptionReference= request.POST['subscriptionID']
            profile.save()
            
        except:
            return JsonResponse({'result':'FAIL'})
    
    elif request.POST['type'] == 'advanced': 
        try:
            profile = Profile.objects.get(uniqueID = request.POST['userId'])
            profile.subscribed= True
            profile.subscriptionType= 'advanced'
            profile.subscriptionReference= request.POST['subscriptionID']
            profile.save()
            
        except:
            return JsonResponse({'result':'FAIL'})
    else:
        return JsonResponse({'result':'FAIL'})
        
    
    #  return redirect (billing)         
        
        


