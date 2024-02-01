from django.urls import path
from . import views

urlpatterns = [
    path('cart/',views.cart,name='cart'), 
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='addtocart'),
    path('order-summary/', views.order_summary, name='order_summary'),
    path('delete_cart_item/<int:cart_item_id>/', views.delete_cart_item, name='delete_cart_item'),
    # path('get_cart_total/', views.get_cart_total, name='get_cart_total'),
    # path('payment/',views.payment,name='payment')


    


    

]
