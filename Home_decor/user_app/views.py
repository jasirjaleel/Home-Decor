from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache,cache_control
from django.contrib import messages
from django.http import JsonResponse
from admin_app.models import Product
from .models import Account
from django.core.mail import send_mail
import random 
# Create your views here.
@never_cache
def home(request):
    return render(request,'user_templates/index.html')

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
        
        
        if Account.objects.filter(username = username).exists():
            messages.success(request,'User Already Exists')
        elif Account.objects.filter(email = email).exists():
            messages.success(request,'Email Already Exists')
        elif pass1 != pass2:
            messages.success(request,'Passwords does not match')
        else:
            myuser = Account.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=pass1)
            myuser.is_active    = False
            myuser.is_admin     = False
            myuser.is_superuser = False
            myuser.is_staff     = False

            myuser.save()
        
        randomotp = str(random.randint(100000, 999999))
        request.session['storedotp'] = randomotp
        request.session['storedemail']=email
        request.session.modified = True 
        request.session.set_expiry(300)

        subject = "Verify Your One-Time Password (OTP) - Home Decor Ecommerce Store"
        sendermail = "noreply@homedecorestore.com"
        otp = f"Dear User,\n\n Your One-Time Password (OTP) for verification is: {randomotp}\n\nThank you for choosing Home Decor Ecommerce Store."
        send_mail(subject,otp,sendermail,[email])
        
        context = {
            'email':email
        }
        # messages.success(request,'Your Account Has Been Successfully Created')
        return render(request,'user_templates/otp.html',context)
    return render(request,'user_templates/sign-up.html')
    
    
@never_cache
def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get('enteredotp')
        storedotp=request.session['storedotp']
        storedemail = request.session['storedemail']

        if otp == storedotp:
            user = Account.objects.get(email=storedemail)
            user.is_active = True
            user.save()
            messages.success(request,'User is Successfully Registered')
            login(request,user)
            return redirect ('home')
        else:
            messages.error(request,'Wrong Entry')
        context = {'email': storedemail}
    return render(request,'user_templates/otp.html',context)


@never_cache
def userlogin(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=="POST":
        email = request.POST.get('email')
        password = request.POST.get('password')  
        user = authenticate(email=email,password=password) 
        if user is not None and  user.is_blocked == False and user.is_superadmin == False:
            login(request,user)
            return redirect('home')
        elif user is not None and user.is_blocked == True:
            messages.error(request,'You are Blocked!')
            return redirect('userlogin')

        else:
            messages.error(request,('There Was An Error Loggin In, Try Again...'))
            return redirect('userlogin')
    else:
        return render(request,'user_templates/login.html')
    

def userlogout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,("You Were Logged Out!"))
    return redirect('userlogin')

def productdetails(request,product_id):
    products = Product.objects.get(id=product_id)
    context = {
        'products':products,
    }
    return render(request,'user_templates/productdetails.html',context)

def shop(request):
    products = Product.objects.all().filter(is_available=True)
    products_count = products.count()
    context  = {
        'products':products,
        'products_count':products_count,
    } 
    return render(request,'user_templates/shop.html',context)

def myaccount(request):
    return render(request,'user_templates/my-account.html')