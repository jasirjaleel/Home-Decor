from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from user_app.models import Account
from .models import *
from django.http import JsonResponse

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

def productdetail(request):
    products = Product.objects.all().order_by('-id')
    product_count = products.count()
    context= {
        'products': products,
        'products_count':product_count,
    }
    return render(request,"admin_templates/products-list.html",context)

@never_cache
def deactivateproduct(request,product_id):
    product = Product.objects.get(id=product_id)
    product.is_available = False
    product.save()
    return redirect('productdetail')

@never_cache
def activateproduct(request,product_id):
    product = Product.objects.get(id=product_id)
    product.is_available = True
    product.save()
    return redirect('productdetail')

def addproduct(request):
    if request.method == "POST":
        productname        = request.POST['product_name']
        category_id        = request.POST['category_id']
        description = request.POST['description']
        price       = request.POST['price']
        stock       = request.POST['stock']
        # productslug        = request.POST['slug']
        image       = request.FILES['image']
      

        category = Category.objects.get(id=category_id)
        product = Product(
            product_name = productname,
            category     = category,
            # slug         = productslug,
            description  = description,
            price        = price,
            stock        = stock,
            images       = image   
        )

        product.save()


        messages.success(request, 'Product Added.')
        return redirect('productdetail')

    categories = Category.objects.all()
    context = {
        'categories':categories
    }
    return render(request,"admin_templates/addproduct.html",context)



@never_cache
@login_required(login_url='userlogin')
def user_management(request):
    if request.user.is_superadmin:
        # if request.method == 'POST':
    #         search_word = request.POST.get('search-box', '')
    #         data = User.objects.filter(Q(username__icontains=search_word)| Q(email__icontains=search_word)).order_by('id').values()
    #     else:
        data = Account.objects.all().order_by('id').exclude(is_superadmin=True)
        context={'users': data}
        return render(request,"admin_templates/usermanagement.html", context=context)
    return redirect('usersignup')
    
    
    # return render(request,"admin_templates/usermanagement.html")
@never_cache
def categorymanagement(request):
    categories = Category.objects.all().order_by('-id')
    # paginator = Paginator(categories,10)
    # page = request.GET.get('page')
    # paged_categories = paginator.get_page(page)
    category_count = categories.count()
    context = {
        'categories':categories,
        # 'categories':paged_categories,
        'category_count':category_count
    }
    return render(request,"admin_templates/categorymanagement.html",context)

@never_cache
@login_required(login_url='adminhome')
def addcategory(request):
    if request.method == "POST":
        category_name = request.POST.get('category_name')
        description   = request.POST.get('category_description')

        category = Category(
            category_name = category_name,
            # slug          = slug,
            description   = description
        )

        category.save()
        return redirect('categorymanagement')
    return render(request,'admin_templates/addcategory.html')


# @never_cache
# def blockuser(request):
#     id = request.GET.get('user_id')
#     user = Account.objects.get(id=id)
#     if request.user.is_authenticated and request.user == user:
#         logout(request)
#         request.session.flush()
#     user.is_blocked = True
#     user.save()
#     messages.success(request,'User is Successfully Blocked')
#     return redirect('user_management')

# @never_cache  
# def unblockuser(request):
#     id = request.GET.get('usr_id')

#     user =  Account.objects.get(id=id)
#     user.is_blocked = False
#     user.save()
#     messages.success(request,'User is unblocked ')
#     return redirect('user_management')



def blockuser(request, user_id):
    user1 = Account.objects.get(id=user_id)
    if user1.is_authenticated :
        logout(request)
        # request.session.flush()
    user1.is_blocked = True
    user1.save()
    # return JsonResponse({'message': 'User blocked successfully'})
    return redirect('user_management')

def unblockuser(request, user_id):
    user = Account.objects.get(id=user_id)
    user.is_blocked = not user.is_blocked 
    user.save()
    # return JsonResponse({'message': 'User unblocked successfully'})
    return redirect('user_management')