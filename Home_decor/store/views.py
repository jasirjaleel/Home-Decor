from django.shortcuts import render,redirect
from product_management.models import Product,Product_Variant,Additional_Product_Image
from category_management.models import Category
from django.db.models import Q
import json
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render, get_object_or_404
# Create your views here.
def home(request):
    return render(request,'store_templates/index.html')

# def productdetails(request, product_id):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         selected_color = data.get('selectedColor')
#         print(selected_color)
#         single_product_variant = Product_Variant.objects.select_related('product').prefetch_related('attributes').filter(id=product_id)
#         white_variants = Product_Variant.objects.filter(attributes__attribute_value=selected_color)
#         print(white_variants)
#         # Add logic to filter variants based on the selected color
#         # and send the filtered data as a JsonResponse
#         return JsonResponse({'status': 'success', 'selectedColor': selected_color})

#     else:
#         single_product_variant = Product_Variant.objects.select_related('product').prefetch_related('attributes').filter(id=product_id)
#         # for i in single_product_variant:
#         for product_variant in single_product_variant:
#             variant = Product_Variant.objects.select_related('product').filter(product=product_variant.product)
#             images  = Additional_Product_Image.objects.filter(product_variant=product_variant.id)
#             # print(variant.product_variant_slug )
#         unique_colors = set()
#         unique_materials = set()    
#         for i in variant:
#             for attribute in i.attributes.all():
#                 if attribute.attribute.attribute_name == 'Color':
#                     unique_colors.add(attribute.attribute_value)
#                 elif attribute.attribute.attribute_name == 'Material':
#                     unique_materials.add(attribute.attribute_value)
#         # for i in variant:
#         #     for attribute in i.attributes.all():
#         #         # if attribute.attribute_value == 'White':
#         #         #     print('h')
#         #         print(attribute.attribute_value)
        
        
        
        
    
            
#         context = {
#             'product': single_product_variant,
#             'variant' : variant,
#             'unique_colors': unique_colors,
#             'unique_materials': unique_materials,
#             'images':images,
#             'product_id':product_id
#         }
#         return render(request,'store_templates/productdetails.html',context)

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


# def productdetails(request, product_id):
#     if request.method == 'POST':
#         print("=======================")
#         data = json.loads(request.body)
#         selected_color = data.get('selectedColor')

#         # Filter variants based on selected color
#         selected_variants = Product_Variant.objects.select_related('product').prefetch_related('attributes').filter(
#             product=product_id,
#             attributes__attribute_value=selected_color
#         )
#         images = Additional_Product_Image.objects.filter(product_variant__in=selected_variants)
        


#         unique_materials = set()
#         for variant in selected_variants:
#             for attribute in variant.attributes.all():
#                 if attribute.attribute.attribute_name == 'Material':
#                     unique_materials.add(attribute.attribute_value)

#         context = {
#             'products': selected_variants,
#             'variant': selected_variants,  # Assuming you want details of the first variant
#             # 'unique_colors': unique_colors,
#             'unique_materials': unique_materials,
#             # 'images': images,
#             'product_id': product_id
#         }

        
#         # Add logic to filter variants based on the selected color
#         # and send the filtered data as a JsonResponse
#         # return JsonResponse({'status': 'success', 'selectedColor': selected_color})
#         # return render(request,'store_templates/productdetails.html',context)
#         return redirect("productdetails2")
#     else:
#         print("+++++++++++++")
#         product_variant = Product_Variant.objects.select_related('product').prefetch_related('attributes').filter(id=product_id)
        
#         # Filter all variants based on the product of the product variant
#         # variants = Product_Variant.objects.select_related('product').filter(product=product_variant.product)
#         # associated_products = [variant.product for variant in product_variant]
#         # variants = Product_Variant.objects.select_related('product').filter(product__in=associated_products)

#         # image_ids = [variant.id for variant in variants]
#         # images = Additional_Product_Image.objects.filter(product_variant__id__in=image_ids)

#         for variant in product_variant:
#             variants = Product_Variant.objects.select_related('product').filter(product=variant.product)
#             images  = Additional_Product_Image.objects.filter(product_variant=variant.id)
#         unique_colors = set()
#         unique_materials = set()

#         for variant in variants:
#             for attribute in variant.attributes.all():
#                 if attribute.attribute.attribute_name == 'Color':
#                     unique_colors.add(attribute.attribute_value)
#                 elif attribute.attribute.attribute_name == 'Material':
#                     unique_materials.add(attribute.attribute_value)

#         context = {
#             # 'products': product_variant,
#             'product': variants.first(),  # Assuming you want details of the first variant
#             'unique_colors': unique_colors,
#             'unique_materials': unique_materials,
#             'images': images,
#             'product_id': product_id
#         }
        
#     return render(request,'store_templates/productdetails.html',context)

# def productdetails(request, product_id):
#     product_variant = Product_Variant.objects.select_related('product').prefetch_related('attributes').filter(id=product_id)

#     for variant in product_variant:
#         variants = Product_Variant.objects.select_related('product').filter(product=variant.product)
#         print(variants)
#         images  = Additional_Product_Image.objects.filter(product_variant=variant.id)
#     unique_colors = set()
#     unique_materials = set()

#     for variant in variants:
#         for attribute in variant.attributes.all():
#             if attribute.attribute.attribute_name == 'Color':
#                 unique_colors.add(attribute.attribute_value)
#             elif attribute.attribute.attribute_name == 'Material':
#                 unique_materials.add(attribute.attribute_value)

#     context = {
#         # 'products': product_variant,
#         'products': variants,  # Assuming you want details of the first variant
#         'unique_colors': unique_colors,
#         'unique_materials': unique_materials,
#         'images': images,
#         'product_id': product_id
#     }
    
    # if request.method == 'POST':
    #     data = json.loads(request.body)
    #     selected_color = data.get('selectedColor')
    #     # Filter variants based on selected color
    #     selected_variants = Product_Variant.objects.select_related('product').prefetch_related('attributes').filter(
    #         product=product_id,
    #         attributes__attribute_value=selected_color
    #     )
    #     images = Additional_Product_Image.objects.filter(product_variant__in=selected_variants)
    #     unique_materials = set()
    #     for variant in selected_variants:
    #         for attribute in variant.attributes.all():
    #             if attribute.attribute.attribute_name == 'Material':
    #                 unique_materials.add(attribute.attribute_value)

    #     context = {
    #         'products2': selected_variants
    # #     }

    # return render(request, 'store_templates/productdetails.html', context)

class ShopView(View):
    template_name = 'store_templates/shop.html'

    def get(self, request):
        products = Product_Variant.objects.all()
        return render(request, self.template_name, {'products': products})

class ProductDetailView(View):
    template_name = 'store_templates/productdetails.html'

    def post(self, request, slug):
         if request.method == 'POST':
            selected_color = self.request.GET.get('selectedColor')
            selected_material = self.request.GET.get('selectedMaterial')


            variants = (
            Product_Variant.objects
            .filter( attributes__attribute__attribute_name='Color', attributes__attribute_value=selected_color)
            .filter(attributes__attribute__attribute_name='Material', attributes__attribute_value=selected_material)
            )
            
            for i in variants:
               product_slug = i.product_variant_slug
            print(f"Selected Color: {selected_color}, Selected Material: {selected_material}, Product Slug: {product_slug}")


            # request.session['product_slug'] = product_slug
            
            # return redirect(f'http://127.0.0.1:8000/product/{product_slug}/') 
            return redirect('product_detail', slug=product_slug)


    def get(self, request, slug):
        print(slug)
        variants = Product_Variant.objects.select_related('product').prefetch_related('attributes').filter(product_variant_slug=slug)
        print(variants)
        images_list = []
        att_list = []
        for variant in variants:
            # Access the id attribute for each variant
            variant_id = variant.id
            variant_att = variant.attributes.all()
            variant_pro= variant.product
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


        context = {
            'variants'          : variants,
            'images'            : images_list,
            'att_list'          : att_list,
            'unique_colors'     : unique_colors,
            'unique_materials'  : unique_materials,

        }
        return render(request, self.template_name, context)