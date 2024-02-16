from django.urls import path
from . import views
from .views import DeleteBannerView,DeleteCouponView

urlpatterns = [
    path('add-attribute/',views.create_attribute,name='add-attribute'),
    path('add-attribute-value/',views.create_attribute_value,name='add-attribute-value'),
    path('add-brand/',views.create_brand,name='add-brand'),
    path('add-banner/', views.create_banner, name='add-banner'),
    path('add-coupon/', views.create_coupon, name='add-coupon'),

    path('attribute/',views.all_attribute,name='attribute'),
    path('attribute-value/',views.all_attribute_value,name='attribute-values'),
    path('brand/',views.all_brand,name='brand'),
    path('banner/', views.all_banner, name='banner'),
    path('coupon/',views.all_coupon,name='coupon'),

    path('edit-coupon/',views.edit_coupon,name='edit-coupon'),
    path('edit-banner/', views.edit_banner, name='edit-banner'),

    
    path('delete-banner/', DeleteBannerView.as_view(), name='delete-banner'),
    path('delete-coupon/', DeleteCouponView.as_view(), name='delete-coupon'),
    

]
