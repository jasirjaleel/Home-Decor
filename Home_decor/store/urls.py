from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('productdetails/',views.productdetails,name='productdetails'),
    path('shop/',views.shop,name='shop'),
    path('productdetails/<int:product_id>/',views.productdetails,name='productdetails'),
    


    

]
