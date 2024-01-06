from django.urls import path
from . import views

urlpatterns = [
    path('',views.adminhome,name='adminhome'),
    path('logout/',views.adminlogout,name='adminlogout'),
    path('product/',views.productdetail,name='productdetail'),
    path('add-product/',views.addproduct,name='addproduct'),
    
    path('user-management/', views.user_management, name='user_management'),
    path('category-management/',views.categorymanagement,name='categorymanagement'),

    
    
    # path('add_user/', views.add_user, name='add_user'),
    # path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    # path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),

    
    

]
