from django.shortcuts import render,redirect
from account.models import Address
from .models import Order,OrderProduct,PaymentMethod,ShippingAddress,Payment
from cart_app.models import CartItem
from django.contrib.auth.decorators import login_required
import datetime
from django.views.decorators.cache import never_cache
from cart_app.views import _delete_unordered_orders
from order.models import Order,OrderProduct,PaymentMethod,ShippingAddress,Payment

# Create your views here.
@login_required(login_url='userlogin')
def payment(request):
    print('1')
    user = request.user
    _delete_unordered_orders(user)
    address = Address.objects.filter(account=user.id)
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    grandtotal1 = request.session.get('grandtotal')
    print(float(grandtotal1))
    print('2')
    if request.method == "POST":
        print('3')

        selected_payment_method = request.POST.get('payment_method')
        payment_methods_instance = PaymentMethod.objects.get(id=selected_payment_method)
        address = Address.objects.get(is_default=True,account=user)
        shipping_address = ShippingAddress.objects.create(
        first_name       = address.first_name,
        last_name        = address.last_name,
        phone_number     = address.phone_number,
        town_city        = address.town_city,
        street_address   = address.street_address,
        state            = address.state,
        country_region   = address.country_region,
        zip_code         = address.zip_code
        )
        print('4')
        
        grandtotal1 = request.session.get('grandtotal')
   
        payment = Payment.objects.create(
            payment_method      = payment_methods_instance,
            amount_paid         = 0,        
            payment_status     ='PENDING',
            )

        draft_order = Order.objects.create(
            user                = user,
            payment             = payment,
            shipping_address    = shipping_address,
            order_total         = float(grandtotal1),
            order_status        ='New',
            is_ordered          = False,
        )
        print('5')
        print(draft_order.order_number)
        payment.payment_order_id = draft_order.order_number
        print(payment.payment_order_id)
        payment.save()


        cart_items = CartItem.objects.filter(user=user)
        for cart_item in cart_items:
            OrderProduct.objects.create(
                order           = draft_order,
                user            = user,
                product_variant = cart_item.product.get_product_name(),
                quantity        = cart_item.quantity,
                product_price   = float(cart_item.product.total_price()),
                images          = cart_item.product.thumbnail_image,
                ordered         = False,
            )
        draft_order.save()
        print('6')

        return redirect('order_review')
    context={
        'address':address,
        'payment_methods': payment_methods,
    }
    return render(request,'order_templates/payment.html',context)

@login_required(login_url='userlogin')
def order_review(request):
    orders_items = OrderProduct.objects.filter(user=request.user,ordered= False,)
    print(orders_items)
    context= {
        'orders_items':orders_items,
    }
    return render(request,'order_templates/order_review.html',context)


@login_required(login_url='userlogin')
@never_cache
def place_order(request):
    if request.method == 'POST':
        user = request.user
        cart_items = CartItem.objects.filter(user=user)
        for cart_item in cart_items:
            # Reduce the stock of products
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()

        # Mark the order as processed
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        draft_order = Order.objects.filter(user=user, is_ordered=False, order_number__startswith=f"ORD{current_date}")
        print(draft_order)
        for i in draft_order:
            i.is_ordered = True
            i.save()
            order_products = OrderProduct.objects.filter(order=i)
            for order_product in order_products:
                order_product.ordered = True
                order_product.save()
        cart_items.delete()

    return render(request,'order_templates/order_success.html')  # Redirect to a page confirming the order placement



###################### ORDER MANAGEMENT #######################
def all_order(request):
    orders = Order.objects.all()
    context = {
        'orders': orders,
    }
    return render(request, 'admin_templates/all_orders.html', context)


def order_details(request, order_id):
    order = Order.objects.get(id=order_id)
    order_products = OrderProduct.objects.filter(order=order)
    payment = Payment.objects.all()
    for i in payment:
        print(i.payment_order_id)
        print(i.payment_id,i.payment_method)
        
    context = {
        'order': order,
        'order_products': order_products,
    }
    return render(request, 'admin_templates/order_details.html', context)
    

