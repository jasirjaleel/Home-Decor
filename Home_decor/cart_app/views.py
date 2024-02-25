from django.shortcuts import render,redirect,get_object_or_404
from .models import CartItem
from django.contrib import messages
from django.http import JsonResponse
from product_management.models import Product_Variant,Coupon,UserCoupon,Product
from .models import Cart,CartItem,Wishlist,WishlistItem
from order.models import OrderProduct,Order
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
import json
from decimal import Decimal
from django.utils import timezone
from django.shortcuts import get_object_or_404
from wallet.models import Wallet,Transaction
from django.core.cache import cache
from offer_management.models import ProductOffer,CategoryOffer
# Create your views here.
def _cart_id(request):
    # cart = request.session.session_key()
    # print('++++++++++++++++++++++')
    # if not cart:
    #     cart = request.session.create()
    #     # print('|||||||||||||||||||||||||||||||||||||||||||||||||||||||||')
    # return cart
    try:
        cart = request.session['storedemail']  # Try to retrieve the email from the session
    except KeyError:
        # If email is not found in session, fetch it from request.user and store it in session
        user = request.user
        cart = request.session['storedemail'] = user.email
    return cart


# Define the private function for deleting unordered orders
def _delete_unordered_orders(user):
    draft_orders = Order.objects.filter(user=user,is_ordered=False)
    if draft_orders.exists():
        for order in draft_orders:
            if order.payment:
                order.payment.delete()
                print("Order Payment deleted")
            if order.shipping_address:
                order.shipping_address.delete()
                print("Order Shipping Address deleted")
        draft_orders.delete()
        print('deleted orders')

def _delete_unwanted_sessions(request):
    if 'grandtotal' in request.session:
        del request.session['grandtotal']
        print('Deleted grantotal from the session')
    if 'discount_amount' in request.session:
        del request.session['discount_amount']
    print('Deleted unwanted sessions')
        # del request.session['cart_items_count']
       
def _product_offer_price(request):
    cartitems = CartItem.objects.filter(user=request.user).select_related('product').select_related('product__product')
    now = timezone.now()
    offer_price = 0
    
    for cartitem in cartitems:
        product_offer = ProductOffer.objects.filter(product=cartitem.product.product,is_active=True).first()
        print(product_offer,'hello')
        if product_offer:
            final_price = product_offer.calculate_discounted_price(cartitem.product)
            offer_price += final_price * cartitem.quantity
    
    return round(offer_price,2)

def _category_offer_price(request):
    cartitems = CartItem.objects.filter(user=request.user).select_related('product').select_related('product__product')
    now = timezone.now()
    offer_price = 0

    for cartitem in cartitems:
        category_offer = CategoryOffer.objects.filter(category=cartitem.product.product.category,is_active=True).first()

        print(category_offer, 'hello')
        if category_offer:
            final_price = category_offer.calculate_discounted_price(cartitem.product)
            offer_price += final_price * cartitem.quantity

    return round(offer_price, 2)

def _grandtotal_calculation(request):
    total       = 0
    quantity    = 0
    shipping    = 100
    offer       = 0
    # Calculate total, quantity, tax, and grandtotal
    for cart_item in CartItem.objects.filter(user=request.user):
        total += round(cart_item.sub_total(), 2)
        quantity += cart_item.quantity

    categoey_offer = _category_offer_price(request)
    product_offer  = _product_offer_price(request)
    print(categoey_offer,product_offer)
    if categoey_offer < product_offer:
        offer_price = product_offer
    else:
        offer_price = categoey_offer
    if offer_price == 0:
        offer = 0
    else:
        offer = (total - offer_price)
    print(offer)
    tax = round(total / 100 * 5, 0)
    grandtotal = Decimal(round(tax + total + shipping, 2))
    discount_amount = request.session.get('discount_amount')
    if discount_amount:
        discount_amount = round(Decimal(discount_amount),2)
        grandtotal -= discount_amount
    grandtotal-=offer
    print
    
    grandtotal = round(grandtotal, 2)
    return grandtotal,tax,discount_amount,quantity,shipping,total,offer

    

@login_required(login_url='userlogin')
@never_cache
def cart(request):
    _delete_unordered_orders(request.user)
    # _delete_unwanted_sessions(request)
    if 'discount_amount' in request.session:
        del request.session['discount_amount']
    total = 0
    quantity = 0
    cart_items = None
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            return render(request, 'cart_templates/empty-cart.html')
        grandtotal,tax,discount_amount,quantity,shipping,total,offer = _grandtotal_calculation(request)
      
        context = {
            'total' : total,
            'quantity'  : quantity,
            'cart_items': cart_items,
            'tax'       : tax,
            'grandtotal': grandtotal,
            'shipping'  : shipping
        }
        return render(request, 'cart_templates/cart.html',context)
    else:
        return redirect('userlogin')
    


@login_required(login_url='userlogin')
def add_to_cart(request, slug):
    current_user    = request.user
    product         = Product_Variant.objects.get(product_variant_slug=slug)

    if request.user.is_authenticated:
        try:
            print("Getting cart id")
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            print("Creating cart id")
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save()
    
        if product.is_available:
            try:
                cart_item = CartItem.objects.get(user=current_user, product=product)
                # cart_item.quantity += 1
                # if cart_item.product.stock < cart_item.quantity:
                #     messages.error(request, 'Out of Stock')
                # else:
                if request.GET.get('quantity'):
                    quantity1 = int(request.GET.get('quantity'))
                    print(quantity1)
                else:
                    quantity1=1
                
                if quantity1 > product.stock :
                    messages.error(request,'Product Out Of Stock')
                    print('nostock')
                else:
                    print('stock')
                    cart_item.quantity += quantity1
                    cart_item.save()

            except CartItem.DoesNotExist:
                cart_item = CartItem.objects.create(
                    product  = product,
                    quantity = 1,
                    cart     = cart,
                    user     = request.user,
                )
                cart_item.save()
            messages.success(request, "Item added to cart")
            # return render(request, 'cart_templates/cart.html', context)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        else:
            messages.success(request, 'Product is currently unavailable')
            return redirect('shop')

    else:
        messages.error(request, 'You should sign in first to add an item to your cart')
        return redirect('userlogin')



@login_required(login_url='userlogin')
@never_cache
def order_summary(request):
    grandtotal,tax,discount_amount,quantity,shipping,total,offer= _grandtotal_calculation(request)
    # print('Before request body')
    # is_wallet_checked = request.GET.get('isWalletChecked',False)
    # print(is_wallet_checked)
    # if is_wallet_checked == 'true':
    #     print('wallet checked')
    #     wallet = Wallet.objects.get(user=request.user)
    #     wallet_balance = wallet.balance
    #     if wallet.balance <= grandtotal  :  
    #         grandtotal = grandtotal- wallet.balance   
    #         wallet_balance = 0
    #         print('wallet 0')
    #     else:
    #         wallet_balance = wallet.balance - grandtotal
    #         grandtotal     = 0
    #         print('grandtotal 0')
    #     request.session['wallet_balance'] = str(wallet_balance)    
    #     request.session['grandtotal_wallet'] = str(grandtotal)
    # if is_wallet_checked == 'false':
    #     if 'grandtotal_wallet' in request.session:
    #         del request.session['grandtotal_wallet']

    # if 'grandtotal_wallet' in request.session:
    #     grandtotal = request.session['grandtotal_wallet']
    request.session['grandtotal'] = str(grandtotal)
    # Return JSON response
    return JsonResponse({
        'total': total,
        'quantity': quantity,
        'shipping': shipping,
        'tax': tax,
        'grandtotal': grandtotal,
        'offer': offer,
        'discount_amount': request.session.get('discount_amount',0),
    })


def applying_coupon(request):
    if request.method == 'POST':
        discount_amount = None 
        if 'discount_amount' in request.session:
            discount_amount = request.session['discount_amount'] 
        if discount_amount is None :
            data = json.loads(request.body)
            coupon_code = data.get('coupon')
            coupn_dict = {'coupon':coupon_code,}
            cache.set('coupon_code',coupn_dict )
            print(coupon_code)
            grand_total = float(request.session.get('grandtotal'))
            print(grand_total)
        
            try:
                # Attempt to get the Coupon object based on the provided coupon code
                coupon = Coupon.objects.get(coupon_code=coupon_code)
                print(coupon,'1')
            except Coupon.DoesNotExist:
                # Handle the case where the coupon does not exist
                data = {'error': 'Coupon does not exist'}
                return JsonResponse(data, status=200)
            
            try:
                # Attempt to get the UserCoupon object for the current user and coupon
                coupon_usage, created = UserCoupon.objects.get_or_create(
                coupon=coupon,
                user=request.user,
                defaults={'usage_count': 0}  # Set default values for newly created instance
                )   
                print(coupon_usage, '2')
            except UserCoupon.DoesNotExist:
                # Handle the case where the UserCoupon does not exist
                data = {'error': 'UserCoupon does not exist'}
                return JsonResponse(data, status=200)
            discount=coupon.discount_percentage
            if coupon_usage.apply_coupon() and grand_total >= float(coupon.minimum_amount):
                discount_amount = grand_total * discount / 100
                coupon.total_coupons-=1
                coupon.save()
                print(discount_amount, 'Success')
                request.session['discount_amount'] = round(discount_amount,2) 
                data={'discount_amount':discount_amount,'discount':discount}
                print(data,'3')
                return JsonResponse({'success':'Coupon Applied'})
                
            else:
                if coupon.expire_date < timezone.now().date():
                    data={'error':'Coupon expired'}
                    print('Failed')
                    return JsonResponse(data)
                elif grand_total < float(coupon.minimum_amount):
                    data={'error':'Minimum amount required'}
                    print('Failed')
                    return JsonResponse(data)
                elif coupon.total_coupons == 0:
                    data={'error':'Coupon not available'}
                    print('Failed')
                    return JsonResponse(data)
                data={'error':'Maximum uses of the coupon reached'}
                print('Failed')
                return JsonResponse(data)
        else:
            return JsonResponse({'error': 'Coupon already applied'})
        

def delete_coupon(request):
    if request.method == 'POST':
        if 'discount_amount' in request.session:
            coupon1 = cache.get('coupon_code')
            coupon_code = coupon1['coupon']
            print(coupon_code)
            # coupon_obj = Coupon.objects.get(coupon_code=coupon_code)
            usercoupon = UserCoupon.objects.select_related('coupon').get(user=request.user,coupon__coupon_code=coupon_code)
            # print(usercoupon.usage_count)
            usercoupon.usage_count -=1
            print('users coupon usage undone')
            coupon = Coupon.objects.get(coupon_code=coupon_code)
            coupon.total_coupons+=1
            del request.session['discount_amount']
            coupon.save() 
            usercoupon.save()
        return JsonResponse({'success': 'Coupon deleted successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'})

@login_required(login_url='userlogin')
def update_cart(request, cart_item_id, new_quantity):
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
        cart_item.quantity = int(new_quantity)
        cart_item.save()

        response_data = {
            'success': True,
            'message': 'Cart updated successfully',
            'subtotal': cart_item.sub_total(),
        }

    except CartItem.DoesNotExist:
        response_data = {
            'success': False,
            'message': 'Cart item not found',
        }

    return JsonResponse(response_data)

@login_required(login_url='userlogin')
def delete_cart_item(request, cart_item_id):
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
        cart_item.delete()

        response_data = {
            'success': True,
            'message': 'Item deleted successfully',
        }
    except CartItem.DoesNotExist:
        response_data = {
            'success': False,
            'message': 'Item not found',
        }

    return JsonResponse(response_data)

################ WISH LIST ####################
def user_wishlist(request):
    
    wishlist,created = Wishlist.objects.get_or_create(user=request.user)
    wishlistItems = WishlistItem.objects.filter(wishlist=wishlist,is_active=True).order_by('-created_at')
    wishlistItems_count = wishlistItems.count()
    for i in wishlistItems:
        print(i.product.get_product_name())
    # paginator = Paginator(wishlistItems,10)
    # page = request.GET.get('page')
    # paged_wishlist = paginator.get_page(page)
    
    context = {
        'wishlistItems':wishlistItems,
        'wishlistItems_count':wishlistItems_count
    }
    return render(request, 'cart_templates/wishlist.html',context)
    

@login_required(login_url='userlogin')
def add_wishlist(request):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        slug = data.get('variant')
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        try:
            product_variant = Product_Variant.objects.get(product_variant_slug=slug)
            print(product_variant,'++++++++++++++=')
        except Product_Variant.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Product not found"})

        wishlist_item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product_variant)
        # if not created:
        #     wishlist_item.delete()

        return JsonResponse({"status": "success", "message": "Added to wishlist"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request"})

    # # current_user    = request.user
    # # slug = request.GET.get('slug')
    # # product = get_object_or_404(Product_Variant, product_variant_slug=slug)
    # # wishlist, created = Wishlist.objects.get_or_create(user=current_user)
    
    # # # Check if the product is already in the wishlist
    # # if WishlistItem.objects.filter(wishlist=wishlist,product=product).exists():
    # #     return JsonResponse({'message': 'Product is already in the wishlist'}, status=400)
    
    # # # Add the product to the wishlist
    # # WishlistItem.objects.create(wishlist=wishlist, product=product)
    
    # # return JsonResponse({'message': 'Product added to wishlist'}, status=200)

    # return render(request, 'cart_templates/wishlist.html')


##################### Delete User Wishlist ####################
def delete_wishlist(request):
    wishlist_item_id = request.GET.get('wishlistitemId')
    print(wishlist_item_id)
    
    # wishlist = Wishlist.objects.get(user=request.user)  
    wishlist_item = get_object_or_404(WishlistItem, id=wishlist_item_id)
    print(wishlist_item)
    wishlist_item.delete()
    return redirect('wishlist')