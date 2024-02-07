from django.contrib import admin
from .models import PaymentMethod,Order,OrderProduct
# Register your models here.

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('method_name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('method_name',)

admin.site.register(OrderProduct)
admin.site.register(Order)