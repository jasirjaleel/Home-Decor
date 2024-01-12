from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('signup/',views.usersignup,name='usersignup'),
    path('login/',views.userlogin,name='userlogin'),
    path('logout/',views.userlogout,name='userlogout'),
    path('productdetails/',views.productdetails,name='productdetails'),
    path('shop/',views.shop,name='shop'),
    path('verify-otp/',views.verify_otp,name='verify-otp'),
    path('myaccount/',views.myaccount,name='myaccount'),
    path('productdetails/<int:product_id>/',views.productdetails,name='productdetails'),
    


    

]
