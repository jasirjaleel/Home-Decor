from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache,cache_control
from django.contrib import messages
from django.http import JsonResponse
from .models import Account
from django.core.mail import send_mail
import random 
from django.contrib.auth.hashers import check_password
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from cart_app.models import Cart
from cart_app.views import _cart_id

import threading
from django.core.mail import EmailMessage

# Create your views here.


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()



def custom_404_view(request,exception):
    return render(request, 'admin_templates/404.html',status=404)

@never_cache
def usersignup(request):
    if request.method == "POST":
        first_name   = request.POST.get('firstname')
        last_name    = request.POST.get('lastname')
        username     = request.POST.get('username')
        email        = request.POST.get('email')
        pass1        = request.POST.get('password1')
        pass2        = request.POST.get('password2')
        # referalid    = request.POST['referalid']
        
        
        if Account.objects.filter(username = username,is_active=True).exists():
            messages.error(request,'User Already Exists')
        elif Account.objects.filter(email = email,is_active=True).exists():
            messages.error(request,'Email Already Exists')
        elif pass1 != pass2:
            messages.error(request,'Passwords does not match')
        else:
            acc = Account.objects.filter(username=username,is_active=False).exists()
            if acc:
                Account.objects.filter(username=username, is_active=False).delete()
                print("delete")
            else:
                myuser = Account.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=pass1)
                myuser.is_active    = False
                myuser.is_admin     = False
                myuser.is_superuser = False
                myuser.is_staff     = False

                myuser.save()
        
        randomotp = str(random.randint(100000, 999999))

        request.session['storedotp']    = randomotp
        request.session['storedemail']  = email
        request.session.modified = True

        subject = "Verify Your One-Time Password (OTP) - Home Decor Ecommerce Store"
        sendermail = "noreply@homedecorestore.com"
        otp = f"Dear User,\n\n Your One-Time Password (OTP) for verification is: {randomotp}\n\nThank you for choosing Home Decor Ecommerce Store."
        send_mail(subject,otp,sendermail,[email])
        context = {
            'email':email
        }
        return render(request,'user_templates/otp.html',context)
    return render(request,'user_templates/sign-up.html')
    
    
@never_cache
def verify_otp(request):
    if request.method == "POST":
        try:
            otp = request.POST.get('enteredotp')
            storedemail = request.session['storedemail']
            storedotp = request.session['storedotp']
            if otp == storedotp:
                user = Account.objects.get(email=storedemail)
                user.is_active = True
                user.save()
                subject = "Successful Login - Home Decor Ecommerce Store"
                sender_mail = "noreply@homedecorestore.com"
                message = "Dear User,\n\nYour login to Home Decor Ecommerce Store was successful.\n\nThank you for choosing Home Decor Ecommerce Store."

                email = EmailMessage(subject, message, sender_mail, [storedemail])
                email_thread = EmailThread(email)
                email_thread.start()
                login(request,user)

                if request.GET.get('next'):
                    return redirect(request.GET.get('next'))
                else:
                    return redirect('home')
            
            else:
                messages.error(request,'Wrong Entry')
        except Exception as e:
            messages.error(request, str(e))  
        context = {'email': storedemail}
    return render(request,'user_templates/otp.html',context)


# def userlogin(request):
#     if request.user.is_authenticated:
#         return redirect('home')
#     if request.method=="POST":
#         email = request.POST.get('email')
#         password = request.POST.get('password')  
#         if not Account.objects.filter(email=email).exists():
#             messages.error(request,("Email Doesn't exist"))
#         else:
#             account = Account.objects.get(email=email)
#             if not check_password(password,account.password):
#                 messages.error(request, "Incorrect password")
#             else:
#                 user = authenticate(email=email,password=password)
#                 if user is not None and  user.is_blocked == False and user.is_superadmin == False:
#                     login(request,user)
#                     return redirect('home')
#                 elif user is not None and user.is_blocked == True:
#                     messages.error(request,'You are Blocked!')
#                     return redirect('userlogin')
#                 else:
#                     messages.error(request,('There Was An Error Loggin In, Try Again...'))
#                     return redirect('userlogin')
#     else:
#         return render(request,'user_templates/login.html')
@never_cache
def userlogin(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=="POST":
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')  
            user = authenticate(email=email,password=password) 
            if user is not None and  user.is_blocked == False and user.is_superadmin == False:
                login(request,user)
                try:
                    print("Getting cart id")
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                except Cart.DoesNotExist:
                    print("Creating cart id")
                    cart = Cart.objects.create(
                        cart_id = _cart_id(request)
                    )
                    cart.save()
        
                if request.GET.get('next'):
                    return redirect(request.GET.get('next'))
                else:
                    messages.success(request, 'Login Successful')
                    return redirect('home')
            elif user is not None and user.is_blocked == True:
                messages.error(request,'You are Blocked!')
                return redirect('userlogin')

            else:
                messages.error(request,('There Was An Error Loggin In, Try Again...'))
                return redirect('userlogin')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('userlogin') 
    else:
        return render(request,'user_templates/login.html')
    
@never_cache
def userlogout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,("You Were Logged Out!"))
    return redirect('userlogin')




class ForgetPasswordView(View):
    template_name = 'user_templates/forget_password.html'

    def post(self, request, *args, **kwargs):
        email = self.request.POST.get('email')
        random_otp = str(random.randint(100000, 999999))
        self.request.session['storedotp'] = random_otp
        self.request.session['storedemail'] = email
        self.request.session.modified = True 

        subject = "Verify Your One-Time Password (OTP) - Home Decor Ecommerce Store"
        sender_mail = "noreply@homedecorestore.com"
        otp_message = f"Dear User,\n\n Your One-Time Password (OTP) for reset password: {random_otp}\n\nThank you for choosing Home Decor Ecommerce Store."
        # send_mail(subject, otp_message, sender_mail, [email])
        email = EmailMessage(subject, otp_message, sender_mail, [email])
        email_thread = EmailThread(email)
        email_thread.start()

        return redirect('verify_password_login')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class VerifyForgetPasswordView(View):
    template_name = 'user_templates/verify_forget_password.html'

    def post(self, request, *args, **kwargs):
        entered_otp = self.request.POST.get('enteredotp')
        stored_otp = self.request.session.get('storedotp')

        if entered_otp == stored_otp:
            return redirect('new_password_login')

        return render(request, self.template_name)

    def get(self, request, *args, **kwargs):
        if 'storedemail' not in request.session or not request.session['storedemail']:
            return redirect('forget_password_login')

        return render(request, self.template_name)


class EnterNewPasswordView(View):
    template_name = 'user_templates/enter_new_password.html'

    def post(self, request, *args, **kwargs):
        if 'storedemail' not in self.request.session or not self.request.session['storedemail']:
            return redirect('forget_password_login')

        password = self.request.POST.get('password')
        confirm_password = self.request.POST.get('confirm_password')

        if password == confirm_password:
            stored_email = self.request.session.get('storedemail')
            user = Account.objects.get(email=stored_email)
            user.set_password(password)
            user.save()

            subject = "Password Reset Successful - Home Decor Ecommerce Store"
            sender_mail = "noreply@homedecorestore.com"
            message = "Dear User,\n\nYour password reset for Home Decor Ecommerce Store was successful.\n\nIf you did not initiate this password reset, please contact our support team immediately.\n\nThank you for choosing Home Decor Ecommerce Store."
            # send_mail(subject, message, sender_mail, [user.email])
            email = EmailMessage(subject, message, sender_mail, [email])
            email_thread = EmailThread(email)
            email_thread.start()

            messages.success(self.request, "Resetting Password Completed")
            return redirect('userlogin')

        return render(request, self.template_name)

    def get(self, request, *args, **kwargs):
        if 'storedemail' not in self.request.session or not self.request.session['storedemail']:
            return redirect('forget_password_login')

        return render(request, self.template_name)
