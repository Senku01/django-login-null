from django.contrib import admin

from django.urls import path

from .views import *

urlpatterns= [
    path('', home , name = 'home'),
    path('register' , register_attempt, name ='register_attempt'),
    path('login' , login_attempt, name = 'login_attempt'),
    path('token', token_auth, name = 'token_auth'),
    path('success',success, name =' success'),
    # URL pattern for verifying the user's account with the provided auth_token
    path('verify/<auth_token>', verify, name='verify'),
    path('error', error_page , name = 'error' )
]