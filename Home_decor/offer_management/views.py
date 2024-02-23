from django.shortcuts import render,redirect
from .models import ProductOffer,CategoryOffer,Product,Category
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
# Create your views here.
def all_product_offer(request):
    product_offer = ProductOffer.objects.all()
    products_count = product_offer.count()
    paginator = Paginator(product_offer,8)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    context = {
        # 'product_offer':product_offer
        'product_offer':paged_products,
    }
    return render(request,'admin_templates/all_offer_products.html',context)

def create_product_offer(request):
    product = Product.objects.all()
    context = { 'product':product}
    
    if request.method == 'POST':
        offer_name          = request.POST.get('offer_name')
        products             = request.POST.get('product')
        expire_date         = request.POST.get('expire_date')
        discount_percentage = request.POST.get('discount_percentage')
        product_offer_image = request.FILES.get('product_offer_image')
        print(products, discount_percentage, product_offer_image, offer_name, type(discount_percentage) )
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

def toggle_offer_active_status(request):
    if request.method == 'POST':
        try:
            product_offer_id = request.GET.get('id')
            product_offer = ProductOffer.objects.get(id=product_offer_id)
            product_offer.is_active = not product_offer.is_active
            product_offer.save()
            return JsonResponse({'success': True})
        except ProductOffer.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product offer not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        

def all_category_offer(request):
    category_offer = CategoryOffer.objects.all()
    category_offer_count = category_offer.count()
    paginator = Paginator(category_offer,8)
    page = request.GET.get('page')
    paged_category_offer = paginator.get_page(page)
    context = {
        'category_offers':paged_category_offer
    }
    return render(request, 'admin_templates/all_offer_category.html', context)

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
        print(expire_date, categories, discount_percentage, category_offer_image, offer_name, type(discount_percentage))
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
        