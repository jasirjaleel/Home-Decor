from django.urls import path
from . import views

urlpatterns = [
    path('signup/',views.usersignup,name='usersignup'),
    path('login/',views.userlogin,name='userlogin'),
    path('logout/',views.userlogout,name='userlogout'),
    path('verify-otp/',views.verify_otp,name='verify-otp'),
 
]
