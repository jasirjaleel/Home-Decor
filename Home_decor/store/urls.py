from django.urls import path
from . import views
from .views import ShopView, ProductDetailView
urlpatterns = [
    path('',views.home,name='home'),
    # path('productdetails/',views.productdetails,name='productdetails'),
    # path('shop/',views.shop,name='shop'),
    # path('productdetails/<slug:slug>/',views.productdetails,name='productdetails'),
    
    path('shop/', ShopView.as_view(), name='shop'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
  


    

]
