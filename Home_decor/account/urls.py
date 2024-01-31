from django.urls import path
from . import views

urlpatterns = [
    path('',views.my_account,name='myaccount'),

    path('my-address/',views.my_address,name='myaddress'),
    path('add-address/',views.add_address,name='addaddress'),
    path('delete-address/',views.delete_address,name='deleteaddress'),

    path('forget-password/',views.forget_password,name='forget_password'),
    path('verify-forget-password/',views.verif_forget_password,name='verif_forget_password'),
    path('new-password/',views.enter_new_password,name='new_password'),

    path('order/',views.my_order,name='myorder'),
    path('profile/',views.my_profile,name='myprofile'),



]