from django.db import models
from product_management.models import Product_Variant
from user_app.models import Account
# Create your models here.

class Cart(models.Model):
    cart_id    = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    user       = models.ForeignKey(Account, on_delete=models.CASCADE, null=True,related_name='cart_items')
    product    = models.ForeignKey(Product_Variant, on_delete=models.CASCADE)
    cart       = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity   = models.IntegerField(default=1)
    is_active  = models.BooleanField(default=True)


    def sub_total(self):
        return self.quantity * self.product.total_price
    
    def items_count(self):
        return CartItem.objects.filter(cart=self.cart).count()
          

    def __str__(self):
        return self.product.product.product_name


class Wishlist(models.Model):
    user = models.OneToOneField(Account,on_delete=models.CASCADE)
    date_added = models.DateField(auto_now_add=True)
    
    
    def __str__(self):
        return str(self.user)

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist,on_delete=models.CASCADE)
    product = models.ForeignKey(Product_Variant,on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.product)
    