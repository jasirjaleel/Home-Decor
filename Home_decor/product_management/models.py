from django.db import models
from category_management.models import Category
from django.utils.text import slugify
from django.urls import reverse
from django.db.models import UniqueConstraint, Q,F,Avg,Count
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from user_app.models import Account
# Create your models here.

# Atribute Table - COLOR , SIZE
class Attribute(models.Model):
    attribute_name  = models.CharField(max_length=50,unique=True)
    is_active       = models.BooleanField(default=True)

    def __str__(self):
        return self.attribute_name
    
# Atribute Value - RED,BLUE,GREEN, L, XL XXL,XXXL
class Attribute_Value(models.Model):
    attribute       = models.ForeignKey(Attribute,on_delete=models.CASCADE)
    attribute_value = models.CharField(max_length=50,unique=True)
    is_active       = models.BooleanField(default=True)

    def __str__(self):
        return self.attribute_value+"-"+self.attribute.attribute_name
    
# Brand IKEA , HOME DECOR , DOIR 
class Brand(models.Model):
    brand_name  = models.CharField(max_length=50,unique=True)
    is_active   = models.BooleanField(default=True)

    def __str__(self):
        return self.brand_name
     

class Product(models.Model):
    product_name    = models.CharField(max_length=200, unique=True)
    slug            = models.SlugField(max_length=200, unique=True)
    description     = models.TextField(max_length=500, blank=True)
    is_available    = models.BooleanField(default=True)
    base_price      = models.DecimalField(max_digits=8, decimal_places=2)
    brand           = models.ForeignKey(Brand,on_delete=models.CASCADE)
    category        = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        product_slug_name = f'{self.brand.brand_name}-{self.product_name}-{self.category.category_name}'
        base_slug = slugify(product_slug_name)
        counter = Product.objects.filter(slug__startswith=base_slug).count()
        if counter > 0:
            self.product_slug = f'{base_slug}-{counter}'
        else:
            self.slug = base_slug
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.brand.brand_name+"-"+self.product_name 


class Product_VariantManager(models.Manager):
    """
    Custom manager
    """
    def get_all_variant(self,product):
        # variant = super(Product_VariantManager, self).get_queryset().filter(product=product).values('sku_id','atributes__atribute_value','atributes__atribute__atribute_name')
        variant = (
                    super(Product_VariantManager, self)
                    .get_queryset()
                    .filter(product=product)
                    .values('sku_id')
                    # .annotate(
                    #     atribute_value=F('atributes__atribute_value'),
                    #     atribute_name=F('atributes__atribute__atribute_name')
                    # )
                )
        return  variant
    


class Product_Variant(models.Model):
    product              = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='products')
    sku_id               = models.CharField(max_length=30)
    attributes           = models.ManyToManyField(Attribute_Value,related_name='attributes')
    max_price            = models.DecimalField(max_digits=8, decimal_places=2)
    sale_price           = models.DecimalField(max_digits=8, decimal_places=2)
    stock                = models.IntegerField()
    product_variant_slug = models.SlugField(unique=True, blank=True,max_length=200)
    thumbnail_image      = models.ImageField(upload_to='media/product_variant/')
    is_active            = models.BooleanField(default=True)
    created_at           = models.DateTimeField(auto_now_add=True)
    updated_at           = models.DateTimeField(auto_now=True)
    

    objects = models.Manager()
    variants = Product_VariantManager()

    def is_available(self):
        return self.stock > 0
        
    def total_price(self):
        # return self.sale_price + self.product.base_price
        return self.sale_price + self.product.base_price

    def save(self, *args, **kwargs):
        product_variant_slug_name = f'{self.product.brand.brand_name}-{self.product.product_name}-{self.product.category.category_name}-{self.sku_id}'
        base_slug = slugify(product_variant_slug_name)
        counter = Product_Variant.objects.filter(product_variant_slug__startswith=base_slug).count()
        if counter > 0:
            self.product_variant_slug = f'{base_slug}-{counter}'
        else:
            self.product_variant_slug = base_slug
        super(Product_Variant, self).save(*args, **kwargs)

    class Meta:
        constraints = [
            UniqueConstraint(
                name='Unique skuid must be provided',
                fields=['product', 'sku_id'],
                condition=Q(sku_id__isnull=False),
            )
        ]

    def get_url(self):
        return reverse('product-variant-detail',args=[self.product.category.slug,self.product_variant_slug])
    
    def get_product_name(self):
        return f'{self.product.brand} {self.product.product_name} - {", ".join([value[0] for value in self.attributes.all().values_list("attribute_value")])}'
    
    def __str__(self):
        return self.get_product_name()
    

############# FOR ADDITIONAL IMAGES ############
class Additional_Product_Image(models.Model):
    product_variant = models.ForeignKey(Product_Variant,on_delete=models.CASCADE,related_name='additional_product_images')
    image           = models.ImageField(upload_to='media/additional_photos/')
    is_active       = models.BooleanField(default=True)

    def __str__(self):
        return self.image.url
    
################## COUPON ######################
class Coupon(models.Model):
    coupon_code         = models.CharField(max_length=100)
    is_expired          = models.BooleanField(default=False)
    discount_percentage = models.IntegerField(default=10, validators=[MinValueValidator(0), MaxValueValidator(100)])
    minimum_amount      = models.IntegerField(default=400)
    max_uses            = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    expire_date         = models.DateField()
    total_coupons       = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    
    # if number of the coupon is 0 or the expired date is over set it as expired

    def save(self, *args, **kwargs):
        # Get the current date
        current_date = timezone.now().date()
        
        # Compare expire_date with current_date
        if self.total_coupons <= 0 or self.expire_date < current_date:
            self.is_expired = True
        else:
            self.is_expired = False
        # Save the instance
        super().save(*args, **kwargs)


    def __str__(self):
        return self.coupon_code
    

class UserCoupon(models.Model):
    user        = models.ForeignKey(Account, on_delete=models.CASCADE)
    coupon      = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    usage_count = models.IntegerField(default=0)

    def apply_coupon(self):
        if self.coupon.is_expired:
            print('Coupon is expired')
            return False  # Coupon i
        if self.usage_count >= self.coupon.max_uses:
            print('Maximum uses reached')
            return False
        
        self.usage_count += 1
        self.save()
        print('Coupon applied successfully In UserCoupon')
        return True