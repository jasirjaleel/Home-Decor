from django.shortcuts import render,redirect
from account.models import Address
from .models import Order,OrderProduct,PaymentMethod,ShippingAddress,Payment
from cart_app.models import CartItem
from django.contrib.auth.decorators import login_required
import datetime
from django.views.decorators.cache import never_cache
from cart_app.views import _delete_unordered_orders 
from order.models import Order,OrderProduct,PaymentMethod,ShippingAddress,Payment
import razorpay
from django.http import JsonResponse,HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import json
from django.core.serializers import serialize

# Create your views here.
@login_required(login_url='userlogin')
def payment(request):
    print('1')
    user = request.user
    _delete_unordered_orders(user)    
    address1 = Address.objects.filter(account=user.id)
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    print('2')
    payment1 = None
    if request.method == "POST":
        print('3')
        payload = json.loads(request.body)
            
            # Access the data from the payload
        selected_payment_method = payload.get('selected_payment_method')
        print(selected_payment_method)
        # selected_payment_method = int(request.GET.get('payment_method'))  
        # selected_payment_method = request.POST.get('payment_method')

        payment_methods_instance = PaymentMethod.objects.get(id=selected_payment_method)
        print(payment_methods_instance)
        address = Address.objects.get(is_default=True,account=user)
        print(address)
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
        
        grandtotal1 = float(request.session.get('grandtotal'))
        print(grandtotal1)
        

        draft_order = Order.objects.create(
            user                = user,
            # payment             = payment,
            shipping_address    = shipping_address,
            order_total         = grandtotal1,
            order_status        ='New',
            is_ordered          = False,
        )
        print('5')
        print(draft_order.order_number)
        
        if payment_methods_instance.method_name == 'Razorpay':
            client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
            print(settings.RAZOR_PAY_KEY_ID,settings.KEY_SECRET)
            data = {
                'amount':(int(grandtotal1)*100),
                'currency':'INR',
            }
            payment1 = client.order.create(data=data)
            print(payment1)
            payment_order_id = payment1['id']

            payment = Payment.objects.create(
            payment_method      = payment_methods_instance,
            amount_paid         = 0,        
            payment_status      ='PENDING',
            payment_order_id    = payment_order_id 
            )
        else:
            payment = Payment.objects.create(
            payment_method      = payment_methods_instance,
            amount_paid         = 0,        
            payment_status      ='PENDING',
            payment_order_id    = draft_order.order_number
            )    
            # payment = Payment.objects.create(
            # payment_method      = payment_methods_instance,
            # amount_paid         = 0,        
            # payment_status      ='PENDING',
            # payment_order_id    = draft_order.order_number
            # )    
        print("**********************")
        print(payment)
        print("**********************")
        print(payment.payment_order_id)
        payment.save()
        draft_order.payment = payment



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
        return JsonResponse({'message': 'Success', 'context': payment1})
    context = {
        'address': address1,
        'payment_methods': payment_methods,
        'RAZOR_PAY_KEY_ID': settings.RAZOR_PAY_KEY_ID,
    }
    return render(request,'order_templates/payment.html',context)

@login_required(login_url='userlogin')
def order_review(request):
    # if request.method == 'POST':
    #     # Retrieve data from the POST request
    #     payload = request.body
    #     signature = request.headers.get('X-Razorpay-Signature')

    #     # Verify the signature using the Razorpay client
    #     client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
    #     try:
    #         client.utility.verify_webhook_signature(payload, signature)
    #         # Signature verification successful
    #         # Extract payment details from the payload
    #         data = request.POST
    #         razorpay_payment_id = data.get('razorpay_payment_id')
    #         razorpay_order_id = data.get('razorpay_order_id')
    #         # Handle the payment success
    #         # ...
    #         return JsonResponse({'status': 'success'})
    #     except razorpay.errors.SignatureVerificationError:
    #         # Signature verification failed
    #         return JsonResponse({'status': 'error', 'message': 'Signature verification failed'}, status=400)
    # else:
    #     return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)

    #     # payment.payment_status = 'SUCCESS'
    #     # payment.payment_id = razorpay_payment_id
    #     # payment.payment_signature = razorpay_signature
    #     # payment.save()
    #     # print(payment)
    #     # print(payment.payment_order_id)
    #     # print(payment.payment_id)
    #     # print(payment.payment_signature)
    #     # print(payment.payment_status)
    #     # print('payment done')

    #     # client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
    #     # client.utility.verify_payment_signature({
    #     # 'razorpay_order_id': razorpay_order_id,
    #     # 'razorpay_payment_id': razorpay_payment_id,
    #     # 'razorpay_signature': razorpay_signature
    #     # })

    orders_items = OrderProduct.objects.filter(user=request.user,ordered= False,)
    print(orders_items)
    context= {
        'orders_items':orders_items,
    }
    return render(request,'order_templates/order_review.html',context)


@csrf_exempt
def paymenthandler(request):
    print("Payment Handler endpoint reached")
 
    # only accept POST request.
    if request.method == "POST":
        try:
            # Extract payment details from the POST request
            payment_id        = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature         = request.POST.get('razorpay_signature', '')
            print(f'1:{payment_id},2:{razorpay_order_id},3:{signature}')
            # Create a dictionary of payment parameters
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # Verify the payment signature
            client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
            result = client.utility.verify_payment_signature(params_dict)

            if not result :
                # Payment signature verification failed
                # return render(request, 'paymentfail.html')
                return JsonResponse({'message': 'Payment signature verification failed'})
            else:
                # Payment signature verification successful
                # Perform necessary actions after successful payment
                # Example: Capture payment, update database, etc.
                payment = Payment.objects.get(payment_order_id=razorpay_order_id)
                payment.payment_status = 'SUCCESS'
                payment.payment_id = payment_id
                payment.payment_signature = signature
                payment.save()
                
                # Here you can add your logic to handle the payment and update your database accordingly
                
                return redirect('order_review')  # Redirect to success page
        except Exception as e:
            # Exception occurred during payment handling
            print('Exception:', str(e))
            return HttpResponseBadRequest()
    else:
        # Redirect to login page if request method is not POST
        return redirect('payment')



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
        del request.session['grandtotal']
        # del request.session['cart_items_count']
        del request.session['discount_amount']

        
    return render(request,'order_templates/order_success.html')  # Redirect to a page confirming the order placement



###################### ORDER MANAGEMENT #######################
def all_order(request):
    orders = Order.objects.all().order_by('-created_at')
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
   
    order_status = Order.ORDER_STATUS_CHOICES



    context = {
        'order': order,
        'order_products': order_products,
        'order_status': order_status,
    }
    return render(request, 'admin_templates/order_details.html', context)
    


#################### CANCEL ORDER ########################
def cancel_order(request):
    order_id = request.GET.get('order_id')
    order = Order.objects.get(id=order_id,user=request.user)
    if order.order_status != 'Cancelled' and order.order_status != 'Delivered':
        order.order_status = 'Cancelled'
        
    else:
        if order.order_status == 'Delivered':
            order.order_status = 'Returned'
    order.save()       
    
    # if order.created_at < datetime.datetime.now() - datetime.timedelta(days=7):
    print(order.order_status)
    print("##############")
    return redirect('myorder')    

################### RETURN ORDER #################
# def return_order(request):
#     order_id = request.GET.get('order_id')
#     order = Order.objects.get(id=order_id,user=request.user)
#     if order.created_at



