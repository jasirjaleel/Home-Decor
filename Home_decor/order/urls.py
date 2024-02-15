from django.urls import path
from . import views

urlpatterns = [
    path('payment/',views.payment,name='payment'),
    path('order-review/',views.order_review,name='order_review'),
    path('place-order/',views.place_order,name='place_order'),

    path('cancel-order/', views.cancel_order, name='cancel_order'),
    path('paymenthander/',views.paymenthandler,name='paymenthander'),

    

]
