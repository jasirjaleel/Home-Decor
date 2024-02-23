from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from category_management.models import Category
from product_management.models import Product
from django.utils import timezone


class CategoryOffer(models.Model):
    offer_name           = models.CharField(max_length=100)
    expire_date          = models.DateField()
    category             = models.ForeignKey(Category, on_delete=models.CASCADE)  # ForeignKey relationship with Category
    discount_percentage  = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    category_offer_slug  = models.SlugField(max_length=200, unique=True)
    category_offer_image = models.ImageField(upload_to='media/category_offer/images/',blank=True)
    is_active            = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        # Automatically generate the slug from the offer name
        if not self.category_offer_slug:
            self.category_offer_slug = slugify(self.offer_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.offer_name
    
    def calculate_discounted_price(self, product_variant):
        return calculate_discounted_price(product_variant, self.discount_percentage)


    def get_absolute_url(self):
        return reverse('category_offer_detail', kwargs={'slug': self.category_offer_slug})



class ProductOffer(models.Model):
    offer_name          = models.CharField(max_length=100)
    expire_date         = models.DateField()
    product             = models.ForeignKey(Product, on_delete=models.CASCADE)  # ForeignKey relationship with Product
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    product_offer_slug  = models.SlugField(max_length=200, unique=True)
    product_offer_image = models.ImageField(upload_to='media/product_offer/images/',blank=True)
    is_active           = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if self.expire_date < timezone.now().date():
            self.is_active = False 
        # Automatically generate the slug from the offer name
        if not self.product_offer_slug:
            self.product_offer_slug = slugify(self.offer_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.offer_name
    
    def calculate_discounted_price(self, product_variant):
        return calculate_discounted_price(product_variant, self.discount_percentage)

    def get_absolute_url(self):
        return reverse('product_offer_detail', kwargs={'slug': self.product_offer_slug})
    


def calculate_discounted_price(product_variant, discount_percentage):
    """
    Calculate the final price of a product with its variant,
    considering any discounts from the offer.
    """
    base_price = product_variant.product.base_price
    sale_price = product_variant.sale_price
    # Calculate the total price including the base price and variant sale price
    total_price = base_price + sale_price
    # Apply discount if available
    if discount_percentage > 0:
        discount_amount = (discount_percentage / 100) * total_price
        total_price -= discount_amount

    return total_price