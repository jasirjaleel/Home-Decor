from django.urls import path
from . import views
from .views import ShopView, ProductDetailView , ProductUpdateView
from wallet.views import paymenthandler2 as paymenthandlerView


urlpatterns = [
    path('',views.home,name='home'),

    
    path('shop/', ShopView.as_view(), name='shop'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/', ProductUpdateView.as_view(), name='product_update'),
  
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),

    path('paymenthandler2/',paymenthandlerView,name='paymenthandler2')

    

]
