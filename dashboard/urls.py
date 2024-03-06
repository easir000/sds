# from django.urls import path

from django.contrib import admin
from django.urls import include, path

from . import views
from .views import *
from django.conf import settings




urlpatterns = [
   
   path("contact/", views.contactView, name="contact"),
   path("success/", views.successView, name="success"),

   path('lpg', views.lpg, name='lpg'),
   path('website', views.website, name='website'),
   
   
   
    
   path('images', views.generate_image_from_text, name='images'),
   path('home', views.home, name='dashboard'),
   path('profile', views.profile, name='profile'),
   path('<str:ref_code>/', views.profile, name='profile'),
   
   path('delete-blog-topic/<str:uniqueId>/', views.deleteBlogTopic, name='delete-blog-topic'),
   path('generate-blog-from-topic/<str:uniqueId>/', views.createBlogFromTopic, name='generate-blog-from-topic'),
   
   
  
   #Blog Generation Routes 
   path('generate-blog-topic', views.blogTopic, name='blog-topic'),
   path('generate-blog-sections', views.blogSections, name='blog-sections'),
   
   #Saving the blog topic for future resue
   path('save-blog-topic/<str:blogTopic>/', views.saveBlogTopic, name='save-blog-topic'),
   
   path('use-blog-topic/<str:blogTopic>/', views.useBlogTopic, name='use-blog-topic'),
   path('view-generated-blog/<slug:slug>/', views.viewGeneratedBlog, name='view-generated-blog'),
   
   
   
  
   
   
   
   
  
  
   path('billing', views.billing, name='billing'),
   path('534dac52-731d-439d-ac5f-773b29a9bfa4', views.webhook, name='webhook'),
   path('paypal-payment-success', views.PaypalPaymentSuccess, name='payment-success'),
   path('subscription', views.subscription, name='subscription'),
   path('subscribe', views.subscribe, name='subscribe'),
   path('subscribed', views.subscribed, name='subscribed'),
   path('sub', views.end_sub, name='sub'),
   path('payment', views.call_back_url, name='payment'),
  
   path('naturallanguagetoOpenAIAPI', views.NL_TO_API, name='NL to ChalkrAI API'),
   path('naturallanguagetoStripeAPI', views.NL_TO_SAPI, name='NL to Stripe API'),
 
   path('pythontonaturallanguage', views.PL_To_NL, name='Python to natural language'),
   path('calculatetimecomplexity', views.C_T_C, name='Calculate Time Complexity'),
   path('translateprogramminglanguages', views.T_P_L, name='tpl'),
   path('explaincode', views.E_C, name='ec'),
   path('pythonbugfixer', views.P_B_F, name='pbf'),
   path('javaScripthelperchatbot', views.J_H_C, name='jhc'),
   path('javaScripttopython', views.J_T_P, name='jtp'),
   path('writeapythondocstring', views.W_P_D, name='wpd'),
   path('javaScriptonelinefunction', views.J_O_L_F, name='jolf'),
   
   
   
   
   
   path('qa', views.Q_A, name='qa'),
   path('grammarcorrection', views.G_C, name='gc'),
   path('summarizefora2ndgrader', views.Summarize, name='sf2g'),
   path('afpd', views.Ad_From_Product_Description, name='afpd'),
   

   path('englishtootherlanguages', views.E_Translate, name='etol'),
   path('parseunstructureddata', views.Parse_unstructured_data, name='pud'),
   
   
  
   path('productnamegenerator', views.Product_Name_Generator, name='png'),
   path('TL;DRsummarization', views.TL_DR_Summarization, name='tldr'),
   path('Spreadsheetcreator', views.Spreadsheet_Creator, name='sc'),
   path('ML/AIlanguagemodeltutor', views.ML_AI_Language_Model_Tutor, name='mlai'),
   
  
   path('SQLrequest', views.SQL_Request, name='sr'),
   path('Extractcontactinformation', views.Extract_Contact_Information, name='eci'),
  
 
   path('Analogymaker', views.Analogy_Maker, name='am'),
  
   path('Thirdpersonconverter', views.Third_Person_Converter, name='tpc'),
   path('Notestosummary', views.Notes_To_Summary, name='ntc'),
   path('VRfitnessideagenerator', views.VR_Fitness_Idea_Generator, name='vfig'),
   path('EssayOutline', views.Essay_Outline, name='eo'),
   path('Recipecreator', views.Recipe_Creator, name='rc'),
   
   

   path('chat', views.Chat, name='chat'),
   
   # path('chat', chat_view, name='chat'),
   path('Marvsarcasticchatbot', views.Marv_Sarcastic_Chat_Bot, name='mscb'),
  
   path('Restaurantreviewcreator', views.Restaurant_Review_Creator, name='rrc'),
   path('Createstudynotes', views.Create_Study_Notes, name='csn'),
   path('Interviewquestions', views.Interview_Questions, name='iq'),
   
   path('content_generator', views.content_generator, name='content_generator'),
   
 # path('error', error_handler, name='error_handler'),
   path('new_chat', views.new_chat, name='new_chat'),
   path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
   path('edit_message/<int:message_id>/', views.edit_message, name='edit_message'),
   
   path('delete_full_history', views.delete_full_history, name='delete_full_history'),

    path('generatevideo', views.generate_video, name='generate_video'),
]
   
   
   
   
   
   
