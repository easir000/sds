from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='dashboard'),
    path('profile', views.profile, name='profile'),
    path('<str:ref_code>/', views.profile, name='profile'),
    path('results/', views.results, name='result'),
    path('bookmark/<int:hotel_id>/', views.bookmark_hotel, name='bookmark_hotel'),
    path('bookmarks/', views.bookmarked_hotels, name='bookmarked_hotels'),
]
