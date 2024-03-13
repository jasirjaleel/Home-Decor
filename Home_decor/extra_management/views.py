from django.shortcuts import render,redirect
from django.views import View
from product_management.models import Attribute,Attribute_Value,Brand,Coupon
from .models import Banner
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import never_cache
# Create your views here.


#===========ATTRIBUTE MANAGEMENT==================
@never_cache
@login_required(login_url='admin_login')
def all_attribute(request):
    
    atributes = Attribute.objects.all()
    paginator = Paginator(atributes,5)
    page = request.GET.get('page')
    paged_atributes = paginator.get_page(page)
    context = {
        'atributes':paged_atributes
    }
    return render(request, 'admin_templates/all_attribute.html',context)
@login_required(login_url='admin_login')
def create_attribute(request):
    if request.method == 'POST':
        attribute   = request.POST.get('attribute')
        attri = Attribute(attribute_name=attribute)
        attri.save()
        return redirect('attribute')
    return render(request,'admin_templates/add_attribute.html')


#===========ATTRIBUTE VALUE MANAGEMENT==================
@never_cache
@login_required(login_url='admin_login')
def all_attribute_value(request):
    
    atribute_values = Attribute_Value.objects.all()
    context = {
        'atribute_values':atribute_values
    }
    return render(request, 'admin_templates/all_attribute_value.html',context)

@never_cache
@login_required(login_url='admin_login')
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
@never_cache
@login_required(login_url='admin_login')
def all_brand(request):
    brd = Brand.objects.all()
    context = { 'brd':brd }
    return render(request,'admin_templates/all_brand.html',context)

@never_cache
@login_required(login_url='admin_login')
def create_brand(request):
    if request.method == 'POST':
        brand = request.POST.get('brand')
        brd = Brand(brand_name=brand)
        brd.save()
        return redirect('brand')
    return render(request,'admin_templates/add_brand.html')

#===========BANNER MANAGEMENT==================
@never_cache
@login_required(login_url='admin_login')
def all_banner(request):
    banner = Banner.objects.all()
    context = { 'banner':banner }
    return render(request, 'admin_templates/all_banner.html', context)



@never_cache
@login_required(login_url='admin_login')
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

@never_cache
@login_required(login_url='admin_login')
def edit_banner(request):
    banner_id = request.GET.get('id')
    old_banner = Banner.objects.get(id=banner_id)
    if request.method == 'POST':

        banner_name             = request.POST.get('banner_name')
        banner_name_sub         = request.POST.get('banner_name_sub')
        banner_url              = request.POST.get('banner_url')
        button_text             = request.POST.get('button_text')
        image                   = request.FILES.get('banner_image')
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
    



#================= COUPON MANAGEMENT =====================
@never_cache
@login_required(login_url='admin_login')
def all_coupon(request):
    coupon = Coupon.objects.all()
    paginator = Paginator(coupon,8)
    page = request.GET.get('page')
    paged_coupons = paginator.get_page(page)
    context = { 'coupon':paged_coupons }
    return render(request, 'admin_templates/all_coupon.html', context)


@never_cache
@login_required(login_url='admin_login')
def create_coupon(request):
    if request.method == 'POST':
        coupon_code           = request.POST.get('coupon_code')
        discount_percentage   = request.POST.get('discount_percentage')
        minimum_amount        = request.POST.get('minimum_amount')
        max_uses              = request.POST.get('max_uses')
        expire_date           = request.POST.get('expire_date')
        total_coupons         = request.POST.get('total_coupons')
        expire_date = datetime.strptime(expire_date, '%d %b %Y').date()
        coupon = Coupon.objects.create(
            coupon_code         = coupon_code,
            discount_percentage = int(discount_percentage),
            minimum_amount      = int(minimum_amount),
            max_uses            = int(max_uses),
            expire_date         = expire_date,
            total_coupons       = int(total_coupons),
        )
        coupon.save()
        return redirect('coupon')
    return render(request, 'admin_templates/add_coupon.html')

@never_cache
@login_required(login_url='admin_login')
def edit_coupon(request):
    coupon_id = request.GET.get('id')
    old_coupon = Coupon.objects.get(id=coupon_id)
    if request.method == 'POST':
        coupon_code           = request.POST.get('coupon_code')
        discount_percentage   = request.POST.get('discount_percentage')
        minimum_amount        = request.POST.get('minimum_amount')
        max_uses              = request.POST.get('max_uses')
        expire_date           = request.POST.get('expire_date')
        total_coupons         = request.POST.get('total_coupons')
        
        expire_date = datetime.strptime(expire_date, '%d %b %Y').date()
        old_coupon.coupon_code         = coupon_code
        old_coupon.discount_percentage = int(discount_percentage)
        old_coupon.minimum_amount      = int(minimum_amount)
        old_coupon.max_uses            = int(max_uses)
        old_coupon.expire_date         = expire_date
        old_coupon.total_coupons       = int(total_coupons)
        old_coupon.save()
        return redirect('coupon')
    
    return render(request, 'admin_templates/edit_coupon.html', {'old_coupon':old_coupon})

class DeleteCouponView(View):
    def get(self, request):
        coupon_id = request.GET.get('id')
        coupon = Coupon.objects.get(id=coupon_id)
        coupon.delete()
        return redirect('coupon')
    