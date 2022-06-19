"""Defines URL patterns for User""" 

from django.urls import path, include

from . import views

app_name = 'Users' 
urlpatterns = [
    # Include default auth urls.
    path('', include('django.contrib.auth.urls'), name='login'),

    # Registration page.
    path('register/', views.register, name='register'),
]