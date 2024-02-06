from django.urls import path
from . import views

urlpatterns = [
    path('payment/',views.payment,name='payment'),
    path('order-review/',views.order_review,name='order_review'),

    

]
