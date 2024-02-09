from django.shortcuts import render,redirect
from django.views import View
from product_management.models import Attribute,Attribute_Value,Brand
from .models import Banner
# Create your views here.


#===========ATTRIBUTE MANAGEMENT==================
def all_attribute(request):
    
    atributes = Attribute.objects.all()
    context = {
        'atributes':atributes
    }
    return render(request, 'admin_templates/all_attribute.html',context)

def create_attribute(request):
    if request.method == 'POST':
        attribute   = request.POST.get('attribute')
        attri = Attribute(attribute_name=attribute)
        attri.save()
        return redirect('attribute')
    return render(request,'admin_templates/add_attribute.html')


#===========ATTRIBUTE VALUE MANAGEMENT==================

def all_attribute_value(request):
    
    atribute_values = Attribute_Value.objects.all()
    context = {
        'atribute_values':atribute_values
    }
    return render(request, 'admin_templates/all_attribute_value.html',context)


def create_attribute_value(request):
    if request.method == 'POST':
        attribute_id  = request.POST.get('attribute_id')
        attribute_value  = request.POST.get('attribute_value')
        attri = Attribute.objects.get(id=attribute_id)
        attrib = Attribute_Value(attribute_value=attribute_value,attribute=attri)
        attrib.save()
        return redirect('attribute-values')
    
    attr = Attribute.objects.all()
    context = {
        'attr':attr
    }
    return render(request,'admin_templates/add_attribute_value.html',context)



#===========BRAND MANAGEMENT==================

def all_brand(request):
    brd = Brand.objects.all()
    context = { 'brd':brd }
    return render(request,'admin_templates/all_brand.html',context)


def create_brand(request):
    if request.method == 'POST':
        brand = request.POST.get('brand')
        brd = Brand(brand_name=brand)
        brd.save()
        return redirect('brand')
    return render(request,'admin_templates/add_brand.html')



# class ToggleStatusView(View):
#     def get(self, request, model, item_id):
#         model_class = self.get_model_class(model)
#         item = model_class.objects.get(pk=item_id)
#         return render(request, 'toggle_status.html', {'item': item, 'model': model})

#     def post(self, request, model, item_id):
#         model_class = self.get_model_class(model)
#         item = model_class.objects.get(pk=item_id)
#         item.is_active = not item.is_active
#         item.save()
#         return redirect(f'{model}_list')

#     def get_model_class(self, model):
#         model_classes = {
#             'attribute': Attribute,
#             'attribute_value': Attribute_Value,
#             'brand': Brand,
#         }
#         return model_classes.get(model, None)



#===========BANNER MANAGEMENT==================
def all_banner(request):
    banner = Banner.objects.all()
    context = { 'banner':banner }
    return render(request, 'admin_templates/all_banner.html', context)


def create_banner(request):
    if request.method == 'POST':
        banner_name         = request.POST.get('banner_name')
        banner_name_sub     = request.POST.get('banner_name_sub')
        banner_url          = request.POST.get('banner_url')
        button_text         = request.POST.get('button_text')
        image               = request.FILES.get('banner_image')
        banner = Banner.objects.create(banner_name=banner_name, banner_name_sub=banner_name_sub, banner_url=banner_url, button_text=button_text, banner_image=image)
        banner.save()
        return redirect('banner')
    return render(request, 'admin_templates/add_banner.html')

def edit_banner(request):
    print("=====================")
    banner_id = request.GET.get('id')
    print(banner_id)
    old_banner = Banner.objects.get(id=banner_id)
    print(old_banner)
    if request.method == 'POST':
        print("++++++++++++++")
        banner_name             = request.POST.get('banner_name')
        banner_name_sub         = request.POST.get('banner_name_sub')
        banner_url              = request.POST.get('banner_url')
        button_text             = request.POST.get('button_text')
        image                   = request.FILES.get('banner_image')
        print(banner_name,banner_name_sub,banner_url,button_text,image)
        print(image)
        old_banner.banner_name      = banner_name
        old_banner.banner_name_sub  = banner_name_sub
        old_banner.banner_url       = banner_url
        old_banner.button_text      = button_text
        old_banner.banner_image     = image
        old_banner.save()
        return redirect('banner')
    context = { 'old_banner':old_banner }
    return render(request, 'admin_templates/edit_banner.html', context)

class DeleteBannerView(View):
    def get(self, request):
        id = request.GET.get('id')
        banner = Banner.objects.get(id=id)
        banner.delete()
        return redirect('banner')