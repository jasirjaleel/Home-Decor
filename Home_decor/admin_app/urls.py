from django.urls import path
from . import views
from product_management import views as productView
from category_management import views as categoryView

urlpatterns = [
    
    path('',views.adminhome,name='adminhome'),
    path('login/',views.admin_login,name='admin_login'),
    path('logout/',views.adminlogout,name='adminlogout'),


    path('all-product/',productView.all_product,name='all-product'), 
    path('create-product/',productView.create_product,name='create_product'),
    path('add-product-variant/',productView.add_product_variant,name='add_product_variant'),
    # path('edit-product/<int:product_id>',views.editproduct,name='editproduct'),
    path('unlist-product/<int:product_id>/',productView.unlist_product,name='unlist-product'), # Making it unavailable
    path('list-product/<int:product_id>/',productView.list_product,name='list-product'),       # Making it available
    
    path('add-category/',categoryView.add_category,name='addcategory'),
    path('manage-category/',categoryView.manage_category,name='manage_category'),

    path('user-management/', views.user_management, name='user_management'),
    path('blockuser/<int:user_id>/', views.blockuser, name='blockuser'),
    path('unblockuser/<int:user_id>/', views.unblockuser, name='unblockuser'),

    
    
    
    # path('add_user/', views.add_user, name='add_user'),
    # path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    # path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),

    
    

]
