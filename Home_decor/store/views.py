from django.shortcuts import render,redirect
from product_management.models import Product,Product_Variant,Additional_Product_Image,Brand,Attribute_Value
from category_management.models import Category
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from extra_management.models import Banner
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from offer_management.models import ProductOffer,CategoryOffer
from decimal import Decimal

def home(request):
    if 'storedotp' in request.session:
            print('otp deleted')
            del request.session['storedotp']
    if 'storedemail' in request.session:
            print('Email deleted')
            del request.session['storedemail']
    hero_banner = Banner.objects.filter(is_active=True)
    products = Product_Variant.objects.filter(is_active=True,stock__gt=0,product__is_available=True)
    images_dict = {}
    for i in products:
        first_image = Additional_Product_Image.objects.filter(product_variant=i.id).first()
        images_dict[i] = first_image
    context = {'product': images_dict, 'hero_banner': hero_banner} 
    return render(request,'store_templates/index.html',context)


# def store (request,category_slug=None):
#     categories = None
#     product_variants = None
#     # search_query = request.GET.get('query')
#     # price_min = request.GET.get('price-min')
#     # price_max = request.GET.get('price-max')
#     # ratings = request.GET.getlist('RATING')
    
    
#     if category_slug !=None:
#         try:
#             category = Category.objects.filter(cat_slug=category_slug)
#         except Exception as e:
#                 print(e)
#                 return redirect('store')
#         product_variants = Product_Variant.objects.select_related('product').prefetch_related('atributes').filter(product__product_catg=category,is_active=True)
#         product_variants_count = product_variants.count()
#     else:
#         product_variants = Product_Variant.objects.select_related('product').prefetch_related('attributes').filter(is_active=True).annotate(avg_rating=Avg('product_review__rating'))

#         # product_variants_count = product_variants.count()

 
#     # #search
#     # if search_query:
#     #     terms = search_query.split()  # Split the search query into individual terms
#     #     for term in terms:
#     #         product_variants = [
#     #                         product for product in product_variants
#     #                         if term.lower() in product.get_product_name().lower()
#     #                     ]
       
#     # #ratings filter   
#     # if ratings:
#     #     rating_filters = Q()
#     #     for rating in ratings:
#     #         rating_filters |= Q(avg_rating__gte=rating)

#     #     product_variants = product_variants.filter(rating_filters)
    
    
    
#     # #price filter 
#     # if price_min:
#     #     product_variants = product_variants.filter(sale_price__gte=price_min)
#     # if price_max:
#     #     product_variants = product_variants.filter(sale_price__lte=price_max)
        
        
#     # # Get all attribute names from the request avoid certain parameters
#     # attribute_names = [key for key in request.GET.keys() if key not in ['query','page','price-min','price-max','RATING']]
    
#     # #other filter
#     # for attribute_name in attribute_names:
#     #     attribute_values = request.GET.getlist(attribute_name)
#     #     if attribute_values:
#     #         product_variants=product_variants.filter(atributes__atribute_value__in=attribute_values)
    
    
    
    
    
#     # product_variants_count = len(product_variants)
    
  
#     # # paginator start
#     # paginator = Paginator(product_variants,6)
#     # page = request.GET.get('page')
#     # paged_products = paginator.get_page(page)
    
#     context = {'product_variants':product_variants,
#                 #'product_variants':paged_products,
#             #    'product_variants_count':product_variants_count,
#             #    'search_query':search_query,
#             #    'price_min':price_min,
#             #    'price_max':price_max,
#                }
    
#     return render(request, 'store/store.html',context)

class ShopView(View):
    template_name = 'store_templates/shop.html'

    def get(self, request):
        products = Product_Variant.objects.filter(is_active=True,stock__gt=0,product__is_available=True).order_by('id')
        product_offers = ProductOffer.objects.filter(is_active=True)
        category_offers = CategoryOffer.objects.filter(is_active=True)
        categories = Category.objects.filter(is_active=True)
        brands = Brand.objects.filter(is_active=True)
        colors = Attribute_Value.objects.filter(attribute__attribute_name='Color')
        product = None
        selected_brand      =  []
        selected_category   =  []
        selected_color      =  []
        selected_sort       =  []

        brand_list      = request.GET.getlist("brand")
        category_list   = request.GET.getlist("category")
        colors_list     = request.GET.getlist("color")
        min_price       = request.GET.get("min_price")
        max_price       = request.GET.get("max_price")
        sort_by         = request.GET.get("sort_by")
        

        if brand_list:
            products = products.filter(product__brand__in=brand_list,is_active=True)
            selected_brand = [product.product.brand.id for product in products]
        if category_list:
            products = products.filter(product__category_id__in=category_list, is_active=True)
            selected_category = [product.product.category.id for product in products]
        if colors_list:
            products = products.filter(attributes__attribute_value__in=colors_list, is_active=True)
            selected_color = [color for color in colors_list]
        if min_price and max_price:
            products = products.filter(total_price__range=[min_price,max_price])

        if sort_by :
            if sort_by == "price_low_to_high":
                products = products.order_by('sale_price')
            elif sort_by == "price_high_to_low":
                products = products.order_by('-total_price')
            elif sort_by == "newest":
                products = products.order_by('-id')
            elif sort_by == "oldest":
                products = products.order_by('id')
            elif sort_by == "a_z":
                products = products.order_by('product__product_name')
            elif sort_by == "z_a":
                products = products.order_by('-product__product_name')
            # elif sort_by == "rating":
            #     products = products.order_by('-product__avg_rating')
            # elif sort_by == "discount":
            #     products = products.order_by('-discount_percentage')
            selected_sort.append(sort_by)
    
        for product in products:
            total_price = product.total_price
            max_discount_price = total_price
            best_offer = None
            for offer in product_offers:
                if offer.product == product.product:
                    offer_discount = (offer.discount_percentage / Decimal(100)) * total_price
                    discounted_price = total_price - offer_discount
                    if discounted_price < max_discount_price:
                        max_discount_price = discounted_price
                        best_offer = offer.discount_percentage
            for category_offer in category_offers:
                if category_offer.category == product.product.category:
                    offer_discount = (category_offer.discount_percentage / Decimal(100)) * total_price
                    discounted_price = total_price - offer_discount
                    if discounted_price < max_discount_price:
                        max_discount_price = discounted_price
                        best_offer = category_offer.discount_percentage
            if best_offer:
                product.discounted_price = max_discount_price
                product.best_offer = best_offer
            else:
                product.discounted_price = total_price
        
        products_count = products.count()
        paginator = Paginator(products,8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        context = {
                'products': paged_products,
                'products_count':products_count,
                
                'categories':categories,
                'brands':brands,
                'colors':colors,
                'selected_brand':selected_brand,
                'selected_category':selected_category,
                'selected_color':selected_color,
                'selected_sort':selected_sort,
                   }
        if product is not None:
            context['discounded_price']=product.discounted_price,
        return render(request, self.template_name, context)

class ProductDetailView(View):
    template_name = 'store_templates/productdetails.html'

    def get(self, request, slug):
        variants = Product_Variant.objects.select_related('product').prefetch_related('attributes').filter(product_variant_slug=slug)
        print(variants.first())
        images_list = []
        att_list = []
        for variant in variants:
            stock = variant.stock
            variant_id = variant.id
            variant_att = variant.attributes.all()
            variant_pro= variant.product
            variant_pro_id= variant.product.id
            # Query the images related to the current variant
            variant_images = Additional_Product_Image.objects.filter(product_variant=variant_id)

        ########################### Calculate discounted price for the current variant based on offers #############################
            total_price = variant.total_price
            max_discount_price = total_price
            best_offer = None

            # Check for product offers
            product_offers = ProductOffer.objects.filter(is_active=True, product=variant_pro)
            for offer in product_offers:
                offer_discount = (offer.discount_percentage / Decimal(100)) * total_price
                discounted_price = total_price - offer_discount
                if discounted_price < max_discount_price:
                    max_discount_price = discounted_price
                    best_offer = offer.discount_percentage

            # Check for category offers
            category_offers = CategoryOffer.objects.filter(is_active=True, category=variant_pro.category)
            for category_offer in category_offers:
                offer_discount = (category_offer.discount_percentage / Decimal(100)) * total_price
                discounted_price = total_price - offer_discount
                if discounted_price < max_discount_price:
                    max_discount_price = discounted_price
                    best_offer = category_offer.discount_percentage
            # Assign the best offer and discounted price to the variant
            variant.discounted_price = max_discount_price
            variant.best_offer = best_offer
            print(variant.discounted_price,total_price)
            print(variant.best_offer)
        ########################################################################################################################
        m = Product_Variant.objects.prefetch_related('attributes').filter(product=variant_pro)
        unique_colors = set()
        unique_materials = set()

        for variant in m:
            # Iterate over related attributes for each variant
            for attribute in variant.attributes.all():
                if attribute.attribute.attribute_name == 'Color':
                    unique_colors.add(attribute.attribute_value)
                elif attribute.attribute.attribute_name == 'Material':
                    unique_materials.add(attribute.attribute_value)
        # print(variant_att)
        for i in variant_att:
             att_list.append(i.attribute_value)
        
        for i in variant_images:
                # Append the queryset to the list
            images_list.append(i.image)

        request.session['variant_pro_id'] = variant_pro_id
        request.session.modified = True

        context = {
            'variants'          : variants,
            'images'            : images_list,
            'att_list'          : att_list,
            'unique_colors'     : unique_colors,
            'unique_materials'  : unique_materials,
            'stock'             : stock,
        }
        return render(request, self.template_name, context)
    

class ProductUpdateView(View):
    # template_name = 'your_template.html'  # Create a template for updating the product


    def post(self, request):
        selected_color = self.request.GET.get('selectedColor')
        selected_material = self.request.GET.get('selectedMaterial')
        variant_pro_id = request.session['variant_pro_id']
        if 'variant_pro_id' in request.session:
            print('variant_pro_id deleted')
            del request.session['variant_pro_id']

        variants = (
            Product_Variant.objects
            .filter(  product=variant_pro_id, attributes__attribute__attribute_name='Color', attributes__attribute_value=selected_color)
            .filter(attributes__attribute__attribute_name='Material', attributes__attribute_value=selected_material)
            )
            
        if variants.exists():
            for i in variants:
                product_slug = i.product_variant_slug
        
            return JsonResponse({'success': True, 'slug': product_slug})
        else:
            return JsonResponse({'success': False, 'errors': 'No matching product variant found.'})