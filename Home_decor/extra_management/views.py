from django.shortcuts import render,redirect
from django.views import View
from product_management.models import Attribute,Attribute_Value,Brand
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


