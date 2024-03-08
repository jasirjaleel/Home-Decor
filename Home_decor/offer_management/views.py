from django.shortcuts import render,redirect
from .models import ProductOffer,CategoryOffer,Product,Category
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
# Create your views here.
@never_cache
@login_required(login_url='admin_login')
def all_product_offer(request):
    product_offer = ProductOffer.objects.all()
    products_count = product_offer.count()
    paginator = Paginator(product_offer,8)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    context = {
        'product_offer':paged_products,
    }
    return render(request,'admin_templates/all_offer_products.html',context)

@never_cache
@login_required(login_url='admin_login')
def create_product_offer(request):
    product = Product.objects.all()
    context = { 'product':product}
    if request.method == 'POST':
        offer_name          = request.POST.get('offer_name')
        products             = request.POST.get('product')
        expire_date         = request.POST.get('expire_date')
        discount_percentage = request.POST.get('discount_percentage')
        product_offer_image = request.FILES.get('product_offer_image')
        expire_date = datetime.strptime(expire_date, '%d %b %Y').date()
        product = Product.objects.get(id=products)
        product_offer = ProductOffer.objects.create( 
            offer_name = offer_name,
            product = product,
            expire_date = expire_date,
            discount_percentage = discount_percentage,
            product_offer_image = product_offer_image
        )
        product_offer.save()
        return redirect('all_products_offer')
    return render(request, 'admin_templates/create_offer_product.html',context)

@never_cache
@login_required(login_url='admin_login')
def edit_product_offer(request):
    product_id = request.GET.get('product_id')
    product = Product.objects.all()
    product_offer = ProductOffer.objects.get(id=product_id)
    context = {
        'product':product,
        'product_offer':product_offer
    }
    if request.method == 'POST':
        offer_name          = request.POST.get('offer_name')
        products            = request.POST.get('product')
        expire_date         = request.POST.get('expire_date')
        discount_percentage = request.POST.get('discount_percentage')
        product_offer_image = request.FILES.get('product_offer_image')
        expire_date         = datetime.strptime(expire_date, '%d %b %Y').date()
        product                             = Product.objects.get(id=products)
        product_offer.offer_name            = offer_name
        product_offer.product               = product
        product_offer.expire_date           = expire_date
        product_offer.discount_percentage   = discount_percentage
        if product_offer_image:
            product_offer.product_offer_image   = product_offer_image
        product_offer.save()
        return redirect('all_products_offer')
    return render(request, 'admin_templates/edit_offer_product.html', context)

@never_cache
@login_required(login_url='admin_login')
def toggle_offer_active_status(request):
    if request.method == 'POST':
        try:
            product_offer_id = request.GET.get('id')
            p = ProductOffer
            product_offer = p.objects.get(id=product_offer_id)
            product_offer.is_active = not product_offer.is_active
            product_offer.save()
            return JsonResponse({'success': True})
        except ProductOffer.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product offer not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
@never_cache
@login_required(login_url='admin_login')
def all_category_offer(request):
    category_offer = CategoryOffer.objects.all()
    paginator = Paginator(category_offer,8)
    page = request.GET.get('page')
    paged_category_offer = paginator.get_page(page)
    context = {
        'category_offers':paged_category_offer
    }
    return render(request, 'admin_templates/all_offer_category.html', context)

@never_cache
@login_required(login_url='admin_login')
def create_category_offer(request):
    category = Category.objects.all()
    context = { 'category':category}
    if request.method == 'POST':
        offer_name           = request.POST.get('offer_name')
        expire_date          = request.POST.get('expire_date')
        categories           = request.POST.get('category')
        discount_percentage  = request.POST.get('discount_percentage')
        category_offer_image = request.FILES.get('category_offer_image')
        expire_date = datetime.strptime(expire_date, '%d %b %Y').date()
        category             = Category.objects.get(id=categories)
        category_offer            = CategoryOffer.objects.create(
            offer_name            = offer_name,
            category              = category,
            expire_date           = expire_date,
            discount_percentage   = discount_percentage,
            category_offer_image  = category_offer_image
        )
        category_offer.save()
        return redirect('all_category_offer')
    return render(request, 'admin_templates/create_offer_category.html',context)

@never_cache
@login_required(login_url='admin_login')
def edit_category_offer(request):
    category_offer_id = request.GET.get('id')
    category = Category.objects.all()
    category_offer = CategoryOffer.objects.get(id=category_offer_id)
    context = {
        'category':category,
        'category_offer':category_offer
    }
    if request.method == 'POST':
        offer_name           = request.POST.get('offer_name')
        expire_date          = request.POST.get('expire_date')
        categories           = request.POST.get('category')
        discount_percentage  = request.POST.get('discount_percentage')
        category_offer_image = request.FILES.get('category_offer_image')
        expire_date = datetime.strptime(expire_date, '%d %b %Y').date()
        category             = Category.objects.get(id=categories)
        category_offer.offer_name            = offer_name
        category_offer.category               = category
        category_offer.expire_date            = expire_date
        category_offer.discount_percentage    = discount_percentage
        if category_offer_image:
            category_offer.category_offer_image  = category_offer_image
        category_offer.save()
        return redirect('all_category_offer')
    return render(request, 'admin_templates/edit_offer_category.html', context)

def toggle_offer_category_status(request):
    if request.method == 'POST':
        try:
            category_offer_id = request.GET.get('id')
            cat_offer = CategoryOffer.objects.get(id=category_offer_id)
            cat_offer.is_active = not cat_offer.is_active
            cat_offer.save()
            return JsonResponse({'success': True})
        except ProductOffer.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product offer not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        