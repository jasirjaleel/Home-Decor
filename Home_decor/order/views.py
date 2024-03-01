from django.shortcuts import render,redirect
from account.models import Address
from .models import Order,OrderProduct,PaymentMethod,ShippingAddress,Payment
from product_management.models import Product_Variant
from cart_app.models import CartItem
from django.contrib.auth.decorators import login_required
import datetime
from django.views.decorators.cache import never_cache
from cart_app.views import _delete_unordered_orders ,_grandtotal_calculation
from order.models import Order,OrderProduct,PaymentMethod,ShippingAddress,Payment
import razorpay
from django.http import JsonResponse,HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import json
from wallet.models import Wallet,Transaction
from decimal import Decimal
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers import serialize

# Create your views here.
# @login_required(login_url='userlogin')
# def payment(request):
#     print('1')
#     user = request.user
#     _delete_unordered_orders(user)    
#     address1 = Address.objects.filter(account=user.id)
#     payment_methods = PaymentMethod.objects.filter(is_active=True)
#     wallet,created = Wallet.objects.get_or_create(user=user)
#     print('2')
#     payment1 = None

    
#     if request.method == "POST":
#         print('3')
#         payload = json.loads(request.body)
#         selected_payment_method = payload.get('selected_payment_method')
#         # if 'wallet_balance' in payload:
#         # wallet_balance = payload.get('wallet_balance')
#         payment_methods_instance = PaymentMethod.objects.get(method_name=selected_payment_method)
#         address = Address.objects.get(is_default=True,account=user)
#         shipping_address = ShippingAddress.objects.create(
#         first_name       = address.first_name,
#         last_name        = address.last_name,
#         phone_number     = address.phone_number,
#         town_city        = address.town_city,
#         street_address   = address.street_address,
#         state            = address.state,
#         country_region   = address.country_region,
#         zip_code         = address.zip_code
#         )
#         print('4')

#         grandtotal,tax,discount_amount,quantity,shipping,total,offer = _grandtotal_calculation(request)
#         print(grandtotal,tax,discount_amount,quantity,shipping,total,offer)
#         # if wallet_balance is not None:
#         #     if wallet.balance <= grandtotal1  :  
#         #         grandtotal1 = grandtotal1- wallet.balance   
#         #         wallet_balance = 0
#         #     else:
#         #         wallet_balance = wallet.balance - grandtotal1
#         #         grandtotal1 = 0
#         #     wallet.balance = wallet_balance
#         #     wallet.save()
#             # Transaction.objects.create(amount=wallet_balance, transaction_type='DEBIT', wallet=wallet)

#         draft_order = Order.objects.create(
#             user                = user,
#             # payment             = payment,
#             order_tax           =   tax,
#             shipping_charge     = shipping,
#             additional_discount = discount_amount,
#             shipping_address    = shipping_address,
#             order_total         = grandtotal,
#             offer               = offer,
#             order_status        = 'New',
#             is_ordered          = False,
#         )
#         print('5')
#         print(draft_order.order_number)
        
#         if payment_methods_instance.method_name == 'Razorpay':
#             client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
#             print(settings.RAZOR_PAY_KEY_ID,settings.KEY_SECRET)
#             data = {
#                 'amount':(int(grandtotal)*100),
#                 'currency':'INR',
#             }
#             payment1 = client.order.create(data=data)
#             print(payment1)
#             payment_order_id = payment1['id']

#             payment = Payment.objects.create(
#             payment_method      = payment_methods_instance,
#             amount_paid         = 0,        
#             payment_status      ='PENDING',
#             payment_order_id    = payment_order_id 
#             )
#         else:
#             payment = Payment.objects.create(
#             payment_method      = payment_methods_instance,
#             amount_paid         = 0,        
#             payment_status      ='PENDING',
#             payment_order_id    = draft_order.order_number
#             )    
#         print("**********************")
#         print(payment)
#         print("**********************")
#         print(payment.payment_order_id)
#         payment.save()
#         draft_order.payment = payment



#         cart_items = CartItem.objects.filter(user=user)
#         for cart_item in cart_items:
#             OrderProduct.objects.create(
#                 order           = draft_order,
#                 user            = user,
#                 product_variant = cart_item.product.get_product_name(),
#                 quantity        = cart_item.quantity,
#                 product_price   = float(cart_item.product.total_price),
#                 images          = cart_item.product.thumbnail_image,
#                 ordered         = False,
#             )
#         draft_order.save()
#         print('6')
#         return JsonResponse({'message': 'Success', 'context': payment1})
#     context = {
#         'address': address1,
#         'payment_methods': payment_methods,
#         'RAZOR_PAY_KEY_ID': settings.RAZOR_PAY_KEY_ID,
#         'wallet': wallet,
#     }
#     return render(request,'order_templates/payment.html',context)

####################################################################
@login_required(login_url='userlogin')
def payment(request):
    if request.method == "POST":
        print('1')
        try:
            user = request.user
            request.session['user'] = str(user)
            _delete_unordered_orders(user)
            print('2')
            payload = json.loads(request.body)
            selected_payment_method = payload.get('selected_payment_method')
            payment_methods_instance = PaymentMethod.objects.get(method_name=selected_payment_method)
            address = Address.objects.get(is_default=True, account=user)
            shipping_address = ShippingAddress.objects.create(
                first_name=address.first_name,
                last_name=address.last_name,
                phone_number=address.phone_number,
                town_city=address.town_city,
                street_address=address.street_address,
                state=address.state,
                country_region=address.country_region,
                zip_code=address.zip_code
            )
            print('3')
            grandtotal, tax, discount_amount, quantity, shipping, total, offer = _grandtotal_calculation(request)
            
            draft_order = Order.objects.create(
                user=user,
                order_tax=tax,
                shipping_charge=shipping,
                additional_discount=discount_amount,
                shipping_address=shipping_address,
                order_total=grandtotal,
                offer=offer,
                order_status='New',
                is_ordered=False,
            )
            print('4')
            # Process payment
            payment = _process_payment(user, draft_order, payment_methods_instance, grandtotal)
            user = request.user
            request.session['user'] = str(user)
            draft_order.payment = Payment.objects.get(payment_order_id=payment['payment_order_id'])
            draft_order.save()
            _create_order_products(draft_order, user)
            print('5')
            return JsonResponse({'message': 'Success', 'context': payment})
        except Exception as e:
            print('Exception:', str(e))
            return HttpResponseBadRequest()
    else:
        # Handle GET request
        user = request.user
        request.session['user'] = str(user)
        _delete_unordered_orders(user)
        address1 = Address.objects.filter(account=user.id)
        payment_methods = PaymentMethod.objects.filter(is_active=True)
        wallet, created = Wallet.objects.get_or_create(user=user)

        context = {
            'address': address1,
            'payment_methods': payment_methods,
            'RAZOR_PAY_KEY_ID': settings.RAZOR_PAY_KEY_ID,
            'wallet': wallet,
        }
        return render(request, 'order_templates/payment.html', context)

def _process_payment(user, draft_order, payment_methods_instance, grandtotal):
    payment = None
    if payment_methods_instance.method_name == 'Razorpay':
        client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
        data = {
            'amount': (int(grandtotal) * 100),
            'currency': 'INR',
        }
        payment1 = client.order.create(data=data)
        payment_order_id = payment1['id']
        payment = Payment.objects.create(
            payment_method=payment_methods_instance,
            amount_paid=0,
            payment_status='PENDING',
            payment_order_id=payment_order_id
        )
        payment1 = {
            'payment_id': payment.id,
            'payment_order_id': payment.payment_order_id,
        }
        return payment1
    else:
        payment = Payment.objects.create(
            payment_method=payment_methods_instance,
            amount_paid=0,
            payment_status='PENDING',
            payment_order_id=draft_order.order_number
        )
        payment_data = {
            'payment_id': payment.id,
            'payment_order_id': payment.payment_order_id,
        }
        return payment_data

def _create_order_products(draft_order, user):
    cart_items = CartItem.objects.filter(user=user)
    for cart_item in cart_items:
        OrderProduct.objects.create(
            order=draft_order,
            user=user,
            product_variant=cart_item.product.get_product_name(),
            quantity=cart_item.quantity,
            product_price=float(cart_item.product.total_price),
            images=cart_item.product.thumbnail_image,
            ordered=False,
        )
    draft_order.save()
####################################################################
@login_required(login_url='userlogin')
def order_review(request):
    orders_items = OrderProduct.objects.filter(user=request.user,ordered= False,)
    print(orders_items)
    context= {
        'orders_items':orders_items,
    }
    return render(request,'order_templates/order_review.html',context)


@csrf_exempt
def paymenthandler(request):
    print("Payment Handler endpoint reached")
    if request.method == "POST":
        try:
            payment_id        = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature         = request.POST.get('razorpay_signature', '')
            print(f'1:{payment_id},2:{razorpay_order_id},3:{signature}')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
            result = client.utility.verify_payment_signature(params_dict)

            if not result :
                return render(request, 'order_templates/paymentfail.html')
                # return JsonResponse({'message': 'Payment signature verification failed'})
            else:
                payment = Payment.objects.get(payment_order_id=razorpay_order_id)
                payment.payment_status = 'SUCCESS'
                payment.payment_id = payment_id
                payment.payment_signature = signature
                order = payment.order.get()
                user = order.user
                payment.amount_paid = order.order_total
                payment.save()
                cart_items = CartItem.objects.filter(user=user)
                for cart_item in cart_items:
                    # Reduce the stock of products
                    product = cart_item.product
                    product.stock -= cart_item.quantity
                    product.save()
                # Mark the order as processed
                current_date = datetime.datetime.now().strftime("%Y%m%d")
                draft_orders = Order.objects.filter(user=user, is_ordered=False, order_number__startswith=f"ORD{current_date}")
                print(draft_orders)
                for draft_order in draft_orders:
                    draft_order.is_ordered = True
                    draft_order.save()
                    order_products = OrderProduct.objects.filter(order=draft_order)
                    for order_product in order_products:
                        order_product.ordered = True
                        order_product.save()
                cart_items.delete()
                # wallet = Wallet.objects.get(user=user)
                # wallet_balance = float(request.session.get('wallet_balance'))
                # wallet.balance = wallet_balance
                # payed_amount = float(request.session.get('grandtotal'))
                # wallet.save()
                # Transaction.objects.create(amount=payed_amount, transaction_type='DEBIT', wallet=wallet)
                session_vars = ['grandtotal', 'discount_amount', 'grandtotal_wallet', 'wallet_balance']
                for var in session_vars:
                    if var in request.session:
                        del request.session[var]
                # Here you can add your logic to handle the payment and update your database accordingly
                return redirect('place_order')   # Redirect to success page
        except Exception as e:
            print('Exception:', str(e))
            # return HttpResponseBadRequest()
            return render(request, 'order_templates/paymentfail.html')
    else:
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
        draft_orders = Order.objects.filter(user=user, is_ordered=False, order_number__startswith=f"ORD{current_date}")
        print(draft_orders)
        for draft_order in draft_orders:
            draft_order.is_ordered = True
            draft_order.save()
            order_products = OrderProduct.objects.filter(order=draft_order)
            for order_product in order_products:
                order_product.ordered = True
                order_product.save()
        cart_items.delete()
        print(request.session['grandtotal'],'hihi')
        session_vars = ['grandtotal', 'discount_amount', 'grandtotal_wallet', 'wallet_balance']
        for var in session_vars:
            if var in request.session:
                del request.session[var]
    return render(request,'order_templates/order_success.html')  # Redirect to a page confirming the order placement

###################### ORDER MANAGEMENT #######################
def all_order(request):
    orders = Order.objects.all().order_by('-created_at').select_related('payment__payment_method')
    paginator = Paginator(orders,5)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    context = {
        # 'orders': orders,
        'orders':paged_orders
    }
    return render(request, 'admin_templates/all_orders.html', context)


def order_details(request, order_id):
    order = Order.objects.select_related('payment').get(id=order_id)
    order_products = OrderProduct.objects.filter(order=order)
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
    if order.payment.payment_status == 'SUCCESS':
        amount = order.order_total
        wallet = Wallet.objects.get(user=request.user)
        wallet.balance += amount
        Transaction.objects.create(wallet=wallet, amount=amount, transaction_type='CREDIT')
        wallet.save()
        order.payment.payment_status = 'REFUNDED'
        order.payment.save()
    else:
        order.payment.payment_status = 'CANCELLED'
        order.payment.save()
    for order_product in order.order_products.all():
        product_variant = order_product.product_variant
        print(product_variant)
        print(order_product.quantity)
        try:
            product_variants = Product_Variant.objects.filter(product__product_name__startswith=product_variant[:3])
            for product_variant_obj in product_variants:
                if product_variant_obj == product_variant:
                    product_variant_obj.stock += order_product.quantity
                    product_variant_obj.save()
                    break
            print(product_variants)
        except Product_Variant.DoesNotExist:
            # Handle case where product variant with given slug/identifier does not exist
            print("Product variant does not exist.")
        else:
            # Update the stock based on order_product.quantity
            # product_variant_obj.stock += order_product.quantity
            print('ho')
            # product_variant_obj.save()
    return redirect('myorder')    
