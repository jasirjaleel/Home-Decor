from django.urls import path
from . import views

urlpatterns = [
    
    path('',views.adminhome,name='adminhome'),
    path('login/',views.admin_login,name='admin_login'),
    path('logout/',views.adminlogout,name='adminlogout'),
    path('product/',views.productdetail,name='productdetail'),
    path('add-product/',views.addproduct,name='addproduct'),
    path('edit-product/<int:product_id>',views.editproduct,name='editproduct'),
    path('add-category/',views.addcategory,name='addcategory'),
    
    path('user-management/', views.user_management, name='user_management'),
    path('category-management/',views.categorymanagement,name='categorymanagement'),

    path('blockuser/<int:user_id>/', views.blockuser, name='blockuser'),
    path('unblockuser/<int:user_id>/', views.unblockuser, name='unblockuser'),

    path('deactivate-product/<int:product_id>/',views.deactivateproduct,name='deactivateproduct'),
    path('activate-product/<int:product_id>/',views.activateproduct,name='activateproduct'),
    
    
    # path('add_user/', views.add_user, name='add_user'),
    # path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    # path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),

    
    

]
