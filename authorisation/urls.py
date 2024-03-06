# from django.urls import path

from django.urls import path,include

from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
   path('login/', views.user_login, name='login/'),
   path('login/', auth_views.LoginView.as_view(template_name='authorisation/login.html'), name='login'),

   path('register', views.user_register, name='register'),
  path("logout", views.user_logout, name="logout"),
  # path("", include('django.contrib.auth.urls')),
  path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

  
 
]