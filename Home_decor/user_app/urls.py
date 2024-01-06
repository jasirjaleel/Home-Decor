from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('signup/',views.usersignup,name='usersignup'),
    path('login/',views.userlogin,name='userlogin'),
    path('logout/',views.userlogout,name='userlogout'),
    path('productdetails/',views.productdetails,name='productdetails'),
    path('shop/',views.shop,name='shop'),
    

]
