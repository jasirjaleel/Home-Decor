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
    if request.user.is_authenticated and request.user.is_superadmin:
        return render(request,"admin_templates/index.html")
    return redirect('home')
    # return render(request,'admin_templates/index.html')

@never_cache
@login_required(login_url='admin_login')
def adminlogout(request):
    logout(request)
    messages.success(request,'Successfuly Logged Out')
    return redirect('home')

@never_cache
@login_required(login_url='userlogin')
def all_users(request):
    if request.user.is_superadmin:
        # if request.method == 'POST':
    #         search_word = request.POST.get('search-box', '')
    #         data = User.objects.filter(Q(username__icontains=search_word)| Q(email__icontains=search_word)).order_by('id').values()
    #     else:
        data = Account.objects.all().order_by('id').exclude(is_superadmin=True)
        context={'users': data}
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


def user_details(request):
    user_id = request.GET.get('user_id')
    user = Account.objects.get(id=user_id)
    address = Address.objects.filter(account=user.id,is_default=True).first()
    ordered_products = OrderProduct.objects.filter(user=user,ordered=True).order_by('-id')

    context={
        "user":user,
        'address':address,
        'ordered_products':ordered_products,
        'ordered_products_count':ordered_products.count()
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