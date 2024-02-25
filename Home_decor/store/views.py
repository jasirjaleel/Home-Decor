from django.shortcuts import render,redirect
from product_management.models import Product,Product_Variant,Additional_Product_Image
from category_management.models import Category
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from extra_management.models import Banner
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from offer_management.models import ProductOffer,CategoryOffer
from decimal import Decimal
# Create your views here.
def home(request):
    if 'storedotp' in request.session:
            print('otp deleted')
            del request.session['storedotp']
    if 'storedemail' in request.session:
            print('Email deleted')
            del request.session['storedemail']
    hero_banner = Banner.objects.filter(is_active=True)
    products = Product_Variant.objects.filter(is_active=True,product__is_available=True)
    images_dict = {}
    for i in products:
        first_image = Additional_Product_Image.objects.filter(product_variant=i.id).first()
        images_dict[i] = first_image
    context = {'product': images_dict, 'hero_banner': hero_banner} 
    return render(request,'store_templates/index.html',context)

# def shop(request):
#     products = Product.objects.all().filter(is_available=True)
#     prod_list = []
#     for i in products:
#         attri = Product_Variant.objects.select_related('product').filter(product=i.id,is_active=True).first()
#         prod_list.append(attri)

#     products_count = len(prod_list)
#     context  = {
#         'products':prod_list,
#         'products_count':products_count,
#     } 
#     return render(request,'store_templates/shop.html',context)


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

        # for product in products:
        #     discounted_price = product.total_price
        #     for offer in product_offers:
        #         if offer.product == product.product:
        #             offer_discount = (offer.discount_percentage / Decimal(100)) * product.total_price
        #             discounted_price -= offer_discount
        #     product.discounted_price = discounted_price
        #     print(product.discounted_price,product.total_price)
        
        for product in products:
            # Calculate the total price of the product
            total_price = product.total_price

            # Initialize variables to hold the maximum discounted price and the corresponding offer
            max_discount_price = total_price
            best_offer = None

            # Check for product offers and find the one with the highest discount
            for offer in product_offers:
                if offer.product == product.product:
                    offer_discount = (offer.discount_percentage / Decimal(100)) * total_price
                    discounted_price = total_price - offer_discount
                    if discounted_price < max_discount_price:
                        max_discount_price = discounted_price
                        best_offer = offer

            # Check for category offers and find the one with the highest discount
            for category_offer in category_offers:
                if category_offer.category == product.product.category:
                    offer_discount = (category_offer.discount_percentage / Decimal(100)) * total_price
                    discounted_price = total_price - offer_discount
                    if discounted_price < max_discount_price:
                        max_discount_price = discounted_price
                        best_offer = category_offer

            # Apply the best offer to the product variant
            if best_offer:
                product.discounted_price = max_discount_price
                product.best_offer = best_offer
            else:
                # No offer found, set the discounted price to the original total price
                product.discounted_price = total_price
            print(product.discounted_price, product.total_price)
            print(product.best_offer)

        products_count = products.count()
        paginator = Paginator(products,8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        return render(request, self.template_name, {'products': paged_products,'products_count':products_count,'discounded_price':product.discounted_price})

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
            'stock': stock

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