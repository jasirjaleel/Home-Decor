from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Create your views here.
def adminhome(request):
    if request.user.is_superuser:
        return render(request,"admin_templates/index.html")
    return redirect('home')
    # return render(request,'admin_templates/index.html')

@never_cache
@login_required(login_url='userlogin')
def adminlogout(request):
    logout(request)
    messages.success(request,'Successfuly Logged Out')
    return redirect('adminhome')

def productdetail(request):
    return render(request,"admin_templates/page-products-list.html")

def addproduct(request):
    return render(request,"admin_templates/page-form-product-1.html")

@never_cache
@login_required(login_url='userlogin')
def user_management(request):
    if request.user.is_superuser:
        # if request.method == 'POST':
    #         search_word = request.POST.get('search-box', '')
    #         data = User.objects.filter(Q(username__icontains=search_word)| Q(email__icontains=search_word)).order_by('id').values()
    #     else:
        data = User.objects.all().order_by('id')
        context={'users': data}
        return render(request,"admin_templates/usermanagement.html", context=context)
    return redirect('usersignup')
    
    
    # return render(request,"admin_templates/usermanagement.html")

def categorymanagement(request):
    return render(request,"admin_templates/categorymanagement.html")