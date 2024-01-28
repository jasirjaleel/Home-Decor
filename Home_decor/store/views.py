from django.shortcuts import render,redirect
from product_management.models import Product,Product_Variant,Additional_Product_Image
from category_management.models import Category

# Create your views here.
def home(request):
    return render(request,'store_templates/index.html')

def productdetails(request, product_id):
    single_product_variant = Product_Variant.objects.select_related('product').prefetch_related('attributes').filter(id=product_id)
    # for i in single_product_variant:
    for product_variant in single_product_variant:
        variant = Product_Variant.objects.select_related('product').filter(product=product_variant.product)
        images  = Additional_Product_Image.objects.filter(product_variant=product_variant.id)
        # print(variant.product_variant_slug )
    
  
        
    context = {
        'products': single_product_variant,
        'variant' : variant,
        'images':images
    }
    return render(request,'store_templates/productdetails.html',context)

def shop(request):
    products = Product.objects.all().filter(is_available=True)
    prod_list = []
    for i in products:
        attri = Product_Variant.objects.select_related('product').filter(product=i.id,is_active=True).first()
        prod_list.append(attri)

    products_count = len(prod_list)
    context  = {
        'products':prod_list,
        'products_count':products_count,
    } 
    return render(request,'store_templates/shop.html',context)


def store (request,category_slug=None):
    categories = None
    product_variants = None
    # search_query = request.GET.get('query')
    # price_min = request.GET.get('price-min')
    # price_max = request.GET.get('price-max')
    # ratings = request.GET.getlist('RATING')
    
    
    if category_slug !=None:
        try:
            category = Category.objects.filter(cat_slug=category_slug)
        except Exception as e:
                print(e)
                return redirect('store')
        product_variants = Product_Variant.objects.select_related('product').prefetch_related('atributes').filter(product__product_catg=category,is_active=True)
        product_variants_count = product_variants.count()
    else:
        product_variants = Product_Variant.objects.select_related('product').prefetch_related('attributes').filter(is_active=True).annotate(avg_rating=Avg('product_review__rating'))

        product_variants_count = product_variants.count()

 
    # #search
    # if search_query:
    #     terms = search_query.split()  # Split the search query into individual terms
    #     for term in terms:
    #         product_variants = [
    #                         product for product in product_variants
    #                         if term.lower() in product.get_product_name().lower()
    #                     ]
       
    # #ratings filter   
    # if ratings:
    #     rating_filters = Q()
    #     for rating in ratings:
    #         rating_filters |= Q(avg_rating__gte=rating)

    #     product_variants = product_variants.filter(rating_filters)
    
    
    
    # #price filter 
    # if price_min:
    #     product_variants = product_variants.filter(sale_price__gte=price_min)
    # if price_max:
    #     product_variants = product_variants.filter(sale_price__lte=price_max)
        
        
    # # Get all attribute names from the request avoid certain parameters
    # attribute_names = [key for key in request.GET.keys() if key not in ['query','page','price-min','price-max','RATING']]
    
    # #other filter
    # for attribute_name in attribute_names:
    #     attribute_values = request.GET.getlist(attribute_name)
    #     if attribute_values:
    #         product_variants=product_variants.filter(atributes__atribute_value__in=attribute_values)
    
    
    
    
    
    # product_variants_count = len(product_variants)
    
  
    # # paginator start
    # paginator = Paginator(product_variants,6)
    # page = request.GET.get('page')
    # paged_products = paginator.get_page(page)
    
    context = {'product_variants':product_variants,
                #'product_variants':paged_products,
            #    'product_variants_count':product_variants_count,
            #    'search_query':search_query,
            #    'price_min':price_min,
            #    'price_max':price_max,
               }
    
    return render(request, 'store/store.html',context)
