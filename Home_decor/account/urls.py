from django.urls import path
from . import views

urlpatterns = [
    path('myaccount/',views.my_account,name='myaccount'),
    path('add-address/',views.add_address,name='addaddress'),
    path('my-address/',views.my_address,name='myaddress'),
    path('order/',views.my_order,name='myorder'),
    path('profile/',views.my_profile,name='myprofile'),



]