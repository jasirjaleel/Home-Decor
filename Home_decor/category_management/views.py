from django.shortcuts import render,redirect
from .models import Category
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required 
# Create your views here.
@never_cache
@login_required(login_url='admin_login')
def manage_category(request):
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
@login_required(login_url='admin_login')
def add_category(request):
    if request.method == "POST":
        category_name = request.POST.get('category_name')

        category = Category(
            category_name = category_name,
            # slug          = slug,
        )

        category.save()
        return redirect('manage_category')
    return render(request,'admin_templates/add_category.html')
