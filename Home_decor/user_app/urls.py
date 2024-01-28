from django.urls import path
from . import views
from .views import ForgetPasswordView, VerifyForgetPasswordView, EnterNewPasswordView


urlpatterns = [
    path('signup/',views.usersignup,name='usersignup'),
    path('login/',views.userlogin,name='userlogin'),
    path('logout/',views.userlogout,name='userlogout'),
    path('verify-otp/',views.verify_otp,name='verify-otp'),
    path('forget-password/', ForgetPasswordView.as_view(), name='forget_password_login'),
    path('verif-forget-password/', VerifyForgetPasswordView.as_view(), name='verify_password_login'),
    path('enter-new-password/', EnterNewPasswordView.as_view(), name='new_password_login'),
 
]
