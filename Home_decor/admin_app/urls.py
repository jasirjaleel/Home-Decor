from django.urls import path
from . import views
from product_management import views as productView
from category_management import views as categoryView
from order import views as orderView

urlpatterns = [
    
    path('',views.adminhome,name='adminhome'),
    path('login/',views.admin_login,name='admin_login'),
    path('logout/',views.adminlogout,name='adminlogout'),


    path('all-product/',productView.all_product,name='all-product'), 
    path('all-variant-product/<int:product_id>/',productView.all_variant_product,name='all-variant-product'), 
    path('create-product/',productView.create_product,name='create_product'),
    path('add-product-variant/',productView.add_product_variant,name='add_product_variant'),
    path('edit-product-variant/<int:product_id>/',productView.edit_product_variant,name='edit_product_variant'),
    path('edit-product/',productView.edit_product,name='edit_product'),
    path('unlist-product/<int:product_id>/',productView.unlist_product,name='unlist-product'), # Making it unavailable
    path('list-product/<int:product_id>/',productView.list_product,name='list-product'),       # Making it available
    path('toggle-product/<int:id>/',productView.toggle_product_variant,name='toggle-product-variant'),       
    
    path('add-category/',categoryView.add_category,name='addcategory'),
    path('manage-category/',categoryView.manage_category,name='manage_category'),

    path('all-users/', views.all_users, name='all-users'),
    path('user-details/', views.user_details, name='user_details'),
    path('blockuser/', views.blockuser, name='blockuser'),
    path('update-order-status/', views.update_order_status, name='update_order_status'),

    path('all-orders/', orderView.all_order, name='all_orders'),
    path('order-details/<int:order_id>/', orderView.order_details, name='order_details'),
    

    
    
    
    # path('add_user/', views.add_user, name='add_user'),
    # path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    # path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),

    
    

]
