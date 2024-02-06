from django.db import models
import datetime
from user_app.models import Account
from account.models import Address
from product_management.models import Product_Variant

# Create your models here.
class PaymentMethod(models.Model):
    method_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.method_name




class Payment(models.Model):
    PAYMENT_STATUS_CHOICES =(
        ("PENDING", "Pending"),
        ("FAILED", "Failed"),
        ("SUCCESS", "Success"),
        )
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100,null=True,blank=True)
    payment_order_id = models.CharField(max_length=100,null=True,blank=True)
    payment_method = models.CharField(max_length=100,null=True,blank=True)
    amount_paid = models.CharField(max_length=30)
    payment_status= models.CharField(choices = PAYMENT_STATUS_CHOICES,max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.payment_id
    


class Order(models.Model):
    ORDER_STATUS_CHOICES =(
        ("New", "New"),
        ("Accepted", "Accepted"),
        ("Delivered", "Delivered"),
        ("Cancelled_Admin", "Cancelled Admin"),
        ("Cancelled_User", "Cancelled User"),
        ("Returned_User", "Returned User"),
        )
    user                = models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    payment             = models.ForeignKey(Payment,on_delete=models.SET_NULL,null=True,blank=True)
    order_number        = models.CharField(max_length=100)
    shipping_address    = models.ForeignKey(Address,on_delete=models.SET_NULL,null=True)
    order_total         = models.DecimalField(max_digits=12, decimal_places=2)
    order_status        = models.CharField(choices = ORDER_STATUS_CHOICES,max_length=20,default='New')
    is_ordered          = models.BooleanField(default=False)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)
    
    # coupon_code = models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True,blank=True)
    # additional_discount = models.IntegerField(default=0,null=True)
    # wallet_discount = models.IntegerField(default=0,null=True)
    # order_note = models.CharField(max_length=100,blank=True,null=True)
    # ip = models.CharField(max_length=50,blank=True)
    @classmethod
    def generate_order_number(cls):
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        last_order = Order.objects.last()
        
        if last_order and last_order.order_number.startswith(current_date):
            sequence_number = int(last_order.order_number[-6:]) + 1
        else:
            sequence_number = 1

        return f"ORD{current_date}{sequence_number:06d}"

    def __str__(self):
        return self.order_number


class OrderProduct(models.Model):

    order           = models.ForeignKey(Order,on_delete=models.CASCADE)
    user            = models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    product         = models.ForeignKey(Product_Variant,on_delete=models.CASCADE)
    quantity        = models.IntegerField()
    # product_price   = models.DecimalField(max_digits=12, decimal_places=2)
    ordered         = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.order)

