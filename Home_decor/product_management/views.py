from django.shortcuts import render,redirect
from django.contrib import messages
from .models import *
from category_management.models import Category
from django.http import JsonResponse
# Create your views here.
##############   DISPLAYING PRODUCT   ############# 
def all_product(request):
    products = Product.objects.all().order_by('-id')
    product_count = products.count()
    context = {
        'products':products,
        'products_count':product_count
    }
    return render(request, 'admin_templates/all_product.html',context)


##############   CREATING NEW PRODUCT   #############
def create_product(request):                                                                        
    category    = Category.objects.all()
    brand       = Brand.objects.all()
    products    = Product.objects.all()

    context= {
        'category'       : category,
        'brand'          : brand,
        'products'       : products,
    }   

    if request.method == "POST":
        product_title   = request.POST.get('product_title')
        category_id     = request.POST.get('category_id')
        brand_id        = request.POST.get('Brand')
        description     = request.POST.get('description')
        base_price     = request.POST.get('price')
        category        = Category.objects.get(id=category_id)
        brand           = Brand.objects.get(id=brand_id)
        
        product = Product(
            product_name = product_title,
            category     = category,
            brand        = brand,
            description  = description, 
            base_price   = base_price
        )

        product.save()
        messages.success(request, 'Product Added.')
        return redirect('all-product')
    

    return render(request,"admin_templates/add_product.html",context)

##############    EDIT PRODUCT    #############
def edit_product(request):     
    product_id = request.GET.get('product_id')
    print(product_id)                                                                   
    category    = Category.objects.all()
    brand       = Brand.objects.all()
    products    = Product.objects.filter(id=product_id)
    products_instance = products.first()

    context= {
        'category'       : category,
        'brand'          : brand,
        'products'       : products_instance,
    }   

    if request.method == "POST":
        product_title   = request.POST.get('product_title')
        category_id     = request.POST.get('category_id')
        brand_id        = request.POST.get('Brand')
        description     = request.POST.get('description')
        base_price      = request.POST.get('price')
        category        = Category.objects.get(id=category_id)
        brand           = Brand.objects.get(id=brand_id)
        
        product                 = Product.objects.filter(id=products_instance.id)
        product.product_name    = product_title
        product.category        = category_id
        product.brand           = brand_id 
        product.description     = description
        product.base_price      = base_price
        product.save()

        messages.success(request, 'Product Edited.')
        return redirect('all-product',product_id.id)
    

    return render(request,"admin_templates/edit_product.html",context)


##############   ALL VARIANT OF PRODUCT   #############

def all_variant_product(request,product_id):
    product         = Product.objects.get(id=product_id)
    product_variant = Product_Variant.objects.filter(product=product)
    context = {
        'product_variant':product_variant,
        
    }
    return render (request,"admin_templates/all_product_variant.html",context)


##############   ADDING VARITION TO A PRODUCT   #############
def add_product_variant(request):
    attributes = Attribute.objects.prefetch_related('attribute_value_set').filter(is_active=True)
    attribute_dict = {}
    for attribute in attributes:
        attribute_values = attribute.attribute_value_set.filter(is_active=True)
        attribute_dict[attribute.attribute_name] = attribute_values  
         #to show how many atribute in frontend
        attribute_values_count = attributes.count()                                                                                 
    category    = Category.objects.all()
    brand       = Brand.objects.all()
    products    = Product.objects.all()


    if request.method == "POST":
        product         = request.POST.get('product')
        sku_id          = request.POST.get('sku_id')
        max_price       = request.POST.get('max_price')
        product_image   = request.FILES.getlist('product_image')
        sale_price      = request.POST.get('sale_price')
        stock           = request.POST.get('stock')      
        thumbnail_image = request.FILES.get('thumbnail_image')
       
        #getting all atributes
        attribute_ids=[]
        for i in range(1,attribute_values_count+1):
            req_atri = request.POST.getlist('attributes')[i-1]
            if req_atri != 'None':
                attribute_ids.append(req_atri)

        product_id =Product.objects.get(id=product)

    
        product_varient = Product_Variant(
            product         = product_id,
            sku_id          = sku_id,
            max_price       = max_price, 
            sale_price      = sale_price, 
            stock           = stock, 
            thumbnail_image = thumbnail_image
        )   
        
        product_varient.save()
        product_varient.attributes.set(attribute_ids)
        for image in product_image:
            Additional_Product_Image.objects.create(product_variant=product_varient,image=image)
            

        messages.success(request, 'Product variation Added.')
        return redirect('create_product')
    

    context= {
        'category': category,
        'brand':brand,
        'products':products,
        'attribute_dict': attribute_dict,
    }

    return render(request,"admin_templates/add_product_variant.html",context)

##############    EDITING PRODUCT VARIANT    #############
def edit_product_variant(request,product_id):
    old_product = Product_Variant.objects.get(id=product_id)
    products =Product.objects.all()

   
    attributes = Attribute.objects.prefetch_related('attribute_value_set').filter(is_active=True)
#    to get the old varient
    attr_values_list = [item['attribute_value'] for item in old_product.attributes.all().values('attribute_value')]
  

    attribute_dict = {}
    for attribute in attributes:
        attribute_values = attribute.attribute_value_set.filter(is_active=True)
        attribute_dict[attribute.attribute_name] = attribute_values  
         #to show how many atribute in fronend
        attribute_values_count = attributes.count()  

        
    if request.method == "POST":
        
        product         = request.POST['product']
        sku_id          = request.POST['sku_id']
        max_price       = request.POST['max_price']
        product_image   = request.FILES.getlist('product_image')
        sale_price      = request.POST['sale_price']
        stock           = request.POST['stock']      
        thumbnail_image = request.FILES.get('existing_product_images')     
       
        #getting all atributes  
        attribute_values = request.POST.getlist('attributes')
       
        attribute_ids = []
        for req_atri in attribute_values:
         if req_atri != 'None':
           attribute_ids.append(req_atri)   

        product_id =Product.objects.get(id=product)
      
        old_product.sku_id          = sku_id
        old_product.max_price       = max_price 
        old_product.sale_price      = sale_price 
        old_product.stock           = stock 

        if thumbnail_image != None:
           old_product.thumbnail_image = thumbnail_image
        else:
           pass   
        
        
        old_product.save()
        old_product.attributes.set(attribute_ids)
        if not product_image  :
            for image in product_image:
                Additional_Product_Image.objects.create(product_variant=old_product,image=image)
        else:
            old_product.additional_product_images.all().delete()
            for image in product_image:
                Additional_Product_Image.objects.create(product_variant=old_product,image=image)
        messages.success(request, 'Product variation Added.')
        return redirect('all-variant-product',product_id=product_id.id)
        # return redirect(request.META.get('HTTP_REFERER', 'all-variant-product'))
     
    
    
    context={
        "old_product":old_product,
        "products": products, 
        'attribute_dict': attribute_dict,
        'attr':attr_values_list,
    }

    return render(request,"admin_templates/edit_product_variant.html",context)

##############   MAKING PRODUCT UNAVAILABLE   #############
def unlist_product(request,product_id):
    product = Product.objects.get(id=product_id)
    product.is_available = False
    product.save()
    return redirect('all-product')

##############   MAKING PRODUCT AVAILABLE   #############
def list_product(request,product_id):
    product = Product.objects.get(id=product_id)
    product.is_available = True
    product.save()
    return redirect('all-product')

##############   UNLIST / LIST PRODUCT VARIANTS   #############
def toggle_product_variant(request,id):
    product_variant = Product_Variant.objects.get(id=id)
    product_variant.is_active = not product_variant.is_active
    product_variant.save()
    response_data = {
        'status': 'success',
        'message': 'Product variant toggled successfully.',
        'product_id': product_variant.product.id,  
    }
    return JsonResponse(response_data)

    