from django.urls import path
from . import views
from wallet.views import wallet as WalletView

urlpatterns = [
    path('',views.my_account,name='myaccount'),
    path('my-address/',views.my_address,name='myaddress'),
    path('my-coupons/',views.my_coupons, name='mycoupons'),
    path('add-address/',views.add_address,name='addaddress'),
    path('delete-address/',views.delete_address,name='deleteaddress'),
    path('edit-address/', views.edit_address, name='editaddress'),

    path('change_password/',views.change_password,name='change_password'),
    path('email_change_password/',views.change_password_with_email,name='email_change_password'),
    path('new-password/',views.enter_new_password,name='new_password'),

    path('wallet/',WalletView, name='wallet'),
    path('order/',views.my_order,name='myorder'),
    path('order-details/',views.order_details,name='order-details'),
    path('profile/',views.my_profile,name='myprofile'),
    path('edit-profile/', views.edit_user_profile, name='editprofile'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),


]