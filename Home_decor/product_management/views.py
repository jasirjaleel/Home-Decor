from django.shortcuts import render,redirect
from django.contrib import messages
from .models import *
from category_management.models import Category
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
    attributes = Attribute.objects.prefetch_related('attribute_value_set').filter(is_active=True)
    attribute_dict = {}
    for attribute in attributes:
        attribute_values = attribute.attribute_value_set.filter(is_active=True)
        attribute_dict[attribute.attribute_name] = attribute_values                                                                                  
    category    = Category.objects.all()
    brand       = Brand.objects.all()
    products    = Product.objects.all()

    context= {
        'category'       : category,
        'brand'          : brand,
        'products'       : products,
        'attribute_dict' : attribute_dict,
    }   

    if request.method == "POST":
        product_title   = request.POST.get('product_title')
        category_id     = request.POST.get('category_id')
        brand_id        = request.POST.get('Brand')
        description     = request.POST.get('description')
        category        = Category.objects.get(id=category_id)
        brand           = Brand.objects.get(id=brand_id)
        
        product = Product(
            product_name = product_title,
            category     = category,
            brand        = brand,
            description  = description, 
        )

        product.save()
        messages.success(request, 'Product Added.')
        return redirect('all-product')
    

    return render(request,"admin_templates/add_product.html",context)


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
    


    print(attributes)
    print(attribute_dict)
    context= {
        'category': category,
        'brand':brand,
        'products':products,
        'attribute_dict': attribute_dict,
    }

    return render(request,"admin_templates/add_product_variant.html",context)

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
