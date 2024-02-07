from django.shortcuts import render,redirect
from account.models import Address
from order.models import PaymentMethod
from .models import Order,OrderProduct
from cart_app.models import CartItem
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='userlogin')
def payment(request):
    print('++++++++++++++++')
    user = request.user
    address = Address.objects.filter(account=user.id)
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    default_address = address.filter(is_default=True)
    default_address_ins = default_address.first()
    grandtotal1 = request.session.get('value',0.00)
    print('++++++++++')
    if request.method == "POST":
        selected_payment_method = request.POST.get('payment_method')
        print(selected_payment_method)
    # grandtotal = request.session.get('grandtotal',{}))
   


        draft_order = Order.objects.create(
            user=user,
            # payment=selected_payment_method,
            shipping_address=default_address_ins,
            order_total=grandtotal1,
            order_status='New',
            is_ordered = False,
        )


        cart_items = CartItem.objects.filter(user=user)
        for cart_item in cart_items:
            OrderProduct.objects.create(
                order=draft_order,
                user=user,
                product=cart_item.product,
                quantity=cart_item.quantity,
                # product_price=cart_item.product.price,
                ordered=False,
            )
        draft_order.save()
        return redirect('order_review')
    context={
        'address':address,
        'payment_methods': payment_methods,
    }
    return render(request,'order_templates/payment.html',context)

@login_required(login_url='userlogin')
def order_review(request):
    orders_items = OrderProduct.objects.filter(user=request.user)
    print(orders_items)
    context= {
        'orders_items':orders_items,
    }
    return render(request,'order_templates/order_review.html',context)


@login_required(login_url='userlogin')
def place_order(request):
    # if request.method == 'POST':
    #     user = request.user
    #     cart_items = CartItem.objects.filter(user=user)
    #     for cart_item in cart_items:
    #         # Reduce the stock of products
    #         product = cart_item.product
    #         product.stock -= cart_item.quantity
    #         product.save()

    #     # Mark the order as processed
    #     draft_order = Order.objects.get(user=user, is_ordered=False)
    #     draft_order.is_ordered = True
    #     draft_order.save()

    #     # Clear the cart
    #     cart_items.delete()

    return render(request,'order_templates/order_success.html')  # Redirect to a page confirming the order placement

    # return redirect('order_review')