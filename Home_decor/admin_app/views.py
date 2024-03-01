from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from user_app.models import Account
from account.models import Address
from .models import *
from django.http import JsonResponse
import json
from order.models import OrderProduct,Order
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from wallet.models import Wallet,Transaction
from product_management.models import Product
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
# Create your views here.


def admin_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email = email , password = password)
        if user is not None and user.is_superadmin == True:
            login(request, user)
            messages.success(request,'Successfuly Logged in')
            return redirect('adminhome')
        else:
            messages.error(request,'Bad Credentials!')
            return render(request,'admin_templates/admin-login.html')
    return render(request,'admin_templates/admin-login.html')

        
@login_required(login_url='admin_login')
def adminhome(request):
    orders = Order.objects.filter(is_ordered=True)
    order_count = orders.count()
    order_total = orders.aggregate(total_order_amount=Sum('order_total'))
    order_total_amount = float(order_total['total_order_amount'])
    products = Product.objects.filter(is_available=True).select_related('category')
    product_count = products.count()
    category_count = products.values('category__category_name').distinct().count()
    context = {
        'order_count'   : order_count,
        'product_count' : product_count,
        'category_count': category_count,
        'order_total'   : order_total_amount,
    }
    return render(request,"admin_templates/index.html",context)

@never_cache
@login_required(login_url='admin_login')
def adminlogout(request):
    logout(request)
    messages.success(request,'Successfuly Logged Out')
    return redirect('home')

@never_cache
@login_required(login_url='admin_login')
def all_users(request):
    if request.user.is_superadmin:
        # if request.method == 'POST':
    #         search_word = request.POST.get('search-box', '')
    #         data = User.objects.filter(Q(username__icontains=search_word)| Q(email__icontains=search_word)).order_by('id').values()
    #     else:
        data = Account.objects.all().order_by('id').exclude(is_superadmin=True)
        paginator = Paginator(data,5)
        page = request.GET.get('page')
        paged_users = paginator.get_page(page)
        context={'users': paged_users }
        return render(request,"admin_templates/all_users.html", context=context)
    return redirect('usersignup')
    

def blockuser(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_user_id = data.get('userId')
        print(selected_user_id)

        if selected_user_id:
            try:
                user = Account.objects.get(id=selected_user_id)
                if user.is_blocked:
                    # User is currently blocked, so unblock
                    user.is_blocked = False
                    user.save()
                    message = 'User unblocked successfully'
                else:
                    # User is not blocked, so block
                    user.is_blocked = True
                    user.save()
                    message = 'User blocked successfully'

                return JsonResponse({'success': True, 'message': message})
            except Account.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found'})
        else:
            return JsonResponse({'success': False, 'message': 'No user ID provided'})

    return render(request, "admin_templates/usermanagement.html", {})
    # if request.user.is_authenticated and request.user == user1:
    #     logout(request)
    #     request.session.flush()
    # user1.is_blocked = True
    # user1.save()
    # # return JsonResponse({'message': 'User blocked successfully'})
    # return redirect('user_management')

@login_required(login_url='admin_login')
def user_details(request):
    user_id = request.GET.get('user_id')
    user = Account.objects.get(id=user_id)
    wallet = Wallet.objects.filter(user=user).first()
    address = Address.objects.filter(account=user.id,is_default=True).first()
    ordered_products = OrderProduct.objects.filter(user=user,ordered=True).order_by('-id')

    context={
        "user":user,
        'address':address,
        'ordered_products':ordered_products,
        'ordered_products_count':ordered_products.count(),
        'wallet':wallet,
    }
    return render(request,'admin_templates/user_details.html',context)

##################### CHANGE ORDER STATUS OF PRODUCT ########################

def update_order_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            new_status = data.get('new_status')
            print(order_id, new_status)

            # Update the order status
            order = Order.objects.get(id=order_id)
            order.order_status = new_status
            order.save()

            return JsonResponse({'message': 'Order status updated successfully'}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

########################## CHART #################################
def fetch_monthly_data(request):
    response = {}
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    current_date = start_date
    while current_date < end_date:
        next_date = current_date + timedelta(days=1)
        purchase_count = Order.objects.filter(created_at__gte=current_date, created_at__lt=next_date, is_ordered=True).count()
        response[current_date.day] = purchase_count
        current_date = next_date
    return JsonResponse({'response': response}, status=200)

def fetch_weekly_data(request):
    response = {}
    end_date = timezone.now()
    start_date = end_date - timedelta(days=6)  
    current_date = start_date
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        purchase_count = Order.objects.filter(created_at__date=current_date, is_ordered=True).count()
        day_name = current_date.strftime("%A")
        response[day_name] = purchase_count
        current_date = next_date
    return JsonResponse({'response':response},status=200)


def fetch_yearly_data(request):
    response = {}
    end_date = timezone.now()
    start_date = end_date.replace(month=1, day=1)
    current_date = start_date
    while current_date <= end_date:
        next_month = current_date.replace(month=(current_date.month + 1))
        purchase_count = Order.objects.filter(
            created_at__gte=current_date, created_at__lt=next_month, is_ordered=True
        ).count()
        month_name = current_date.strftime("%B")
        response[month_name] = purchase_count
        current_date = next_month
    return JsonResponse({'response': response}, status=200)


def fetch_custom_data(request):
    response = {}
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%d-%m-%Y').date() 
        end_date = datetime.strptime(end_date, '%d-%m-%Y').date() 
        current_date = start_date
        while current_date <= end_date:
            purchase_count = Order.objects.filter(created_at__date=current_date, is_ordered=True).count()
            response[str(current_date)] = purchase_count
            current_date += timedelta(days=1)
    return JsonResponse({'response': response}, status=200)