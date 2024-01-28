from django.shortcuts import render,redirect
from .models import Address
from user_app.models import Account
from django.http import JsonResponse
import json
from django.core.mail import send_mail
import random
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import login
# Create your views here.

def my_account(request):
    return render(request,'account_templates/my-account.html')

 
def my_address(request):
    user = request.user
    address = Address.objects.filter(account=user)

    if request.method == 'POST':
        data = json.loads(request.body)
        selected_address_id = data.get('addressId')

        # print(selected_address_id)
        if selected_address_id:
            try:
                selected_address = Address.objects.get(pk=selected_address_id)
                selected_address.is_default = True
                selected_address.save()

                # Update other addresses to set is_default=False
                Address.objects.filter(account=user).exclude(pk=selected_address_id).update(is_default=False)

                return JsonResponse({'success': True, 'message': 'Address set as default successfully'})
            except Address.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Selected address not found'})
        else:
            return JsonResponse({'success': False, 'message': 'No address ID provided'})

    context = {'address': address}
    return render(request, 'account_templates/my-address.html', context)


def add_address(request):
    if request.method == "POST":
        first_name       = request.POST.get('first_name')
        last_name        = request.POST.get('last_name')
        phone_number     = request.POST.get('phone_number')
        town_city        = request.POST.get('town_city')
        street_address   = request.POST.get('street_address')
        state            = request.POST.get('state')
        country_region   = request.POST.get('country_region')
        zip_code         = request.POST.get('zip_code')
        user=request.user
        address = Address.objects.create(account=user,first_name=first_name,last_name=last_name,phone_number=phone_number,town_city=town_city,street_address=street_address,state=state,country_region=country_region,zip_code=zip_code)
        make_default = request.POST.get('make_default')
        print(make_default)
        # Convert 'on' to True and set is_default accordingly
        is_default = make_default == 'on'
        address.is_default = is_default
        address.save()
        return redirect('myaddress')
    return render(request,'account_templates/add-address.html')

def my_order(request):
    return render(request,'account_templates/orders.html')

def my_profile(request):
    return render(request,'account_templates/my-profile.html')

 
def forget_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        # if email == request.user
        print(request.user)
        randomotp = str(random.randint(100000, 999999))
        request.session['storedotp'] = randomotp
        request.session['storedemail']=email
        request.session.modified = True 
        request.session.set_expiry(600)

        subject = "Verify Your One-Time Password (OTP) - Home Decor Ecommerce Store"
        sendermail = "noreply@homedecorestore.com"
        otp = f"Dear User,\n\n Your One-Time Password (OTP) for reset password: {randomotp}\n\nThank you for choosing Home Decor Ecommerce Store."
        send_mail(subject,otp,sendermail,[email])
        return redirect ('verif_forget_password')
    return render(request,'account_templates/forget_password.html')



def verif_forget_password(request):
    if 'storedemail' not in request.session or not request.session['storedemail']:
        return redirect('forget_password')
    if request.method == "POST":
        otp = request.POST.get('enteredotp')
        storedotp=request.session['storedotp']

        if otp == storedotp:
            return redirect ('new_password')
    return render(request,'account_templates/verify_forget_password.html')


# @login_required(login_url='userlogin') 
def enter_new_password(request):
    if 'storedemail' not in request.session or not request.session['storedemail']:
        return redirect('forget_password')
    if request.method == "POST":
        password           = request.POST.get('password')
        confirm_password   = request.POST.get('confirm_password')
        if password == confirm_password:
    
            userr = request.user         # Assuming you have a custom user model (Account)
            userr.set_password(password)
            userr.save()
            login(request, userr)
            subject = "Password Reset Successful - Home Decor Ecommerce Store"
            sender_mail = "noreply@homedecorestore.com"
            message = "Dear User,\n\nYour password reset for Home Decor Ecommerce Store was successful.\n\nIf you did not initiate this password reset, please contact our support team immediately.\n\nThank you for choosing Home Decor Ecommerce Store."
            send_mail(subject, message, sender_mail,[userr])
            messages.success(request, "Resetting Password Completed")
            return redirect('myaccount')
    return render(request,'account_templates/enter_new_password.html')
    
            # Account.objects.get()
            # account = Account.objects.update(password=password)
            # account.save()
