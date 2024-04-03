from django.shortcuts import render,redirect
from .models import Address
from user_app.models import Account
from product_management.models import Coupon,UserCoupon
from django.http import JsonResponse
import json
from django.core.mail import send_mail
import random
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from order.models import Order, OrderProduct
from django.db.models import Count
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.db.models import F,Sum,Q
from django.utils import timezone
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
        is_default = make_default == 'on'
        address.is_default = is_default
        address.save()
        # return redirect(request.META.get('HTTP_REFERER', 'myaddress')) # To redirect back to the page it came from 
        next_url = request.GET.get('next', 'myaddress')
        return redirect(next_url)
        # return redirect('myaddress')
    return render(request,'account_templates/add-address.html')

def delete_address(request):
    address_id = request.GET.get('id')
    address = get_object_or_404(Address, id = address_id)
    user_address = Address.objects.filter(first_name = address.first_name )
    if not user_address:
        return redirect('myaddress')
    user_address.delete()
    messages.success(request, 'Address deleted successfully.')
    return redirect('myaddress')

def my_order(request):
    user = request.user
    orders = Order.objects.filter(user=user,is_ordered=True).order_by('-created_at')
    orders = orders.annotate(item_count=Count('order_products'))
    context = {
        'orders': orders,
        }
    return render(request,'account_templates/my-orders.html',context)

###################### ORDER DERAIL PAGE ########################
def order_details(request):
    order_id = request.GET.get('order_id')
    order = Order.objects.get(id=order_id, user=request.user)
    order_products = OrderProduct.objects.filter(order=order)
    order_status = Order.ORDER_STATUS_CHOICES
    context = {
        'order': order,
        'order_products': order_products,
        'order_status': order_status,
        'order_id':order_id
    }
    return render(request, 'account_templates/order_details.html', context)

def my_profile(request):
    print(request.user)
    account = Account.objects.filter(email=request.user)
    address = Address.objects.filter(account=request.user)
    acc=account.first()
    print(address.count())
    context = {
        "account":acc,
        "address":address.count(),
    }
    
    return render(request,'account_templates/my-profile.html',context)

@never_cache
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = request.user
        if check_password(old_password, user.password):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully.')
                return redirect('myaccount')
            else:
                messages.error(request, 'New password and confirm password do not match.')
        else:
            messages.error(request, 'Old password is incorrect.')
    return render(request,'account_templates/change_password.html')

@never_cache
def change_password_with_email(request):
    randomotp = str(random.randint(100000, 999999))
    
    subject = "Verify Your One-Time Password (OTP) - Home Decor Ecommerce Store"
    sendermail = "noreply@homedecorestore.com"
    otp = f"Dear User,\n\n Your One-Time Password (OTP) for reset password: {randomotp}\n\nThank you for choosing Home Decor Ecommerce Store."
    send_mail(subject,otp,sendermail,[request.user.email])
    if request.method == "POST":    
        otp = request.POST.get('otp')
        print(otp)
        if otp == randomotp:
            messages.success(request, 'OTP verified successfully.')
        return redirect('new_password')
    return render(request,'account_templates/change_password_with_email.html')

# @login_required(login_url='userlogin') 
@never_cache
def enter_new_password(request):
    if request.method == "POST":
        password           = request.POST.get('password')
        confirm_password   = request.POST.get('confirm_password')
        if password == confirm_password:
    
            userr = request.user  
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

####################### EDIT USER PROFILE #####################
def edit_user_profile(request):
    user = request.user
    account = Account.objects.get(email=user)
    if request.method == "POST":
        first_name       = request.POST.get('first_name')
        last_name        = request.POST.get('last_name')
        phone_number     = request.POST.get('phone_number')
        print(first_name,last_name,phone_number)


        new_account = Account.objects.get(email=request.user)
        new_account.first_name = first_name
        new_account.last_name = last_name
        new_account.phone_number = phone_number
        new_account.save()
        return redirect('myprofile') 
    context = {
        'account': account,
    } 
    return render(request, 'account_templates/edit_user_profile.html',context)


#################### EDIT ADDRESS #####################
def edit_address(request):
    user = request.user
    address_id = request.GET.get('address_id')
    address = Address.objects.get(account=user,id=address_id)
    if request.method == "POST":
        first_name       = request.POST.get('first_name')
        last_name        = request.POST.get('last_name')
        phone_number     = request.POST.get('phone_number')
        town_city        = request.POST.get('town_city')
        street_address   = request.POST.get('street_address')
        state            = request.POST.get('state')
        country_region   = request.POST.get('country_region')
        zip_code         = request.POST.get('zip_code')
    
        new_address = Address.objects.get(account=user,id=address_id)
        new_address.first_name      = first_name
        new_address.last_name       = last_name
        new_address.phone_number    = phone_number
        new_address.town_city       = town_city
        new_address.street_address  = street_address
        new_address.state           = state
        new_address.country_region  = country_region
        new_address.zip_code        = zip_code
        new_address.save()
        return redirect('myaddress')
    context = {
        "address":address,
    }
    return render(request, 'account_templates/edit-address.html',context)


def generate_pdf(request):
    order_id = request.GET.get('order_id')
    order = Order.objects.get(id=order_id, user=request.user)
    order_products = OrderProduct.objects.filter(order=order)
    order_status = Order.ORDER_STATUS_CHOICES
    context = {
        'order': order,
        'order_products': order_products,
        'order_status': order_status,
        'order_id':order_id
    }
    html = render_to_string("account_templates/invoice.html", context)
    pdf_response = HttpResponse(content_type="application/pdf")
    pdf_response["Content-Disposition"] = f'filename="{order.order_number}_invoice.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=pdf_response)
    if pisa_status.err:
        return HttpResponse('Failed to generate PDF: %s' % pisa_status.err)

    return pdf_response

def my_coupons(request):
    user = request.user
    coupons = Coupon.objects.filter(is_expired=False)
    # # available_coupons = UserCoupon.objects.filter(user=user,coupon__in=coupons)
    # coupons = Coupon.objects.annotate(
    #     total_usage_count=Sum('usercoupon__usage_count', filter=Q(usercoupon__user=user))
    # ).filter(
    #     is_expired=False,
    #     total_coupons__gt=F('total_usage_count')
    # )
    
    
    print(coupons)
    context = { 
       'coupons':coupons,
    }
    return render(request, 'account_templates/coupons.html', context)