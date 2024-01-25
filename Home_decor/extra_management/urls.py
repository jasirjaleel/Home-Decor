from django.urls import path
from . import views

urlpatterns = [
    path('add-attribute/',views.create_attribute,name='add-attribute'),
    path('add-attribute-value/',views.create_attribute_value,name='add-attribute-value'),
    path('add-brand/',views.create_brand,name='add-brand'),


    path('attribute/',views.all_attribute,name='attribute'),
    path('attribute-value/',views.all_attribute_value,name='attribute-values'),
    path('brand/',views.all_brand,name='brand'),


    


    

]
