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



# def addproduct(request):
#     if request.method == "POST":
#         productname   = request.POST['product_name']
#         category_id   = request.POST['category_id']
#         description   = request.POST['description']
#         price         = request.POST['price']
#         stock         = request.POST['stock']
#         # productslug = request.POST['slug']
#         image         = request.FILES['image']              


        # category = Category.objects.get(id=category_id)
#         product = Product(
#             product_name = productname,
#             category     = category,
#             # slug         = productslug,
#             description  = description,
#             price        = price,
#             stock        = stock,
#             images       = image   
#         )

#         product.save()


#         messages.success(request, 'Product Added.')
#         return redirect('productdetail')

#     categories = Category.objects.all()
#     context = {
#         'categories':categories
#     }
#     return render(request,"admin_templates/addproduct.html",context)


# @never_cache
# @login_required(login_url='adminhome')
# def editproduct(request,product_id):
#     if request.method ==  "POST":

#         productname        = request.POST['product_name']
#         productslug        = slugify(productname)
#         productdescription = request.POST['description']
#         productprice       = request.POST['price']
#         productstock       = request.POST['stock']
#         productimages      = request.FILES.get('image')
#         productcategory    = request.POST['category_id']

#         category = Category.objects.get(id=productcategory)

#         product              = Product.objects.get(id=product_id)
#         product.product_name = productname
#         product.slug         = productslug
#         product.description  = productdescription
#         product.stock        = productstock
#         product.category     = category
#         product.price        = productprice
#         product.offerprice   = productprice

#         if productimages is not None:
#             product.images = productimages
#         product.save()
#         messages.success(request,'Successfully Saved')
#         return redirect('productdetail')

        
#     category = Category.objects.all()


#     pros = Product.objects.get(id=product_id)
#     context = {
#         'product':pros,
#         'category':category,
#     }

#     return render(request,'admin_templates/editproduct.html',context)



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


def blockuser(request, user_id):
    user1 = Account.objects.get(id=user_id)
    if request.user.is_authenticated and request.user == user1:
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