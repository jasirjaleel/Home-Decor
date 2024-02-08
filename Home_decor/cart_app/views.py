from django.shortcuts import render,redirect
from .models import CartItem
from django.contrib import messages
from django.http import JsonResponse
from product_management.models import Product_Variant
from .models import Cart,CartItem
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
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


@login_required(login_url='userlogin')
@never_cache
def cart(request):
    total = 0
    quantity = 0
    cart_items = None

    if request.user.is_authenticated:
        tax = 0
        grandtotal = 0
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            return render(request, 'cart_templates/empty-cart.html')
        
        for cart_item in cart_items:
            total += round(cart_item.sub_total(), 2)
            quantity += cart_item.quantity
        shipping = 100
        tax = round(total / 100 * 5, 2)
        grandtotal = round(tax + total + shipping, 2)
        request.session['grandtotal'] = str(grandtotal)
      
        context = {
            'total' : total,
            'quantity'  : quantity,
            'cart_items': cart_items,
            'tax'       : tax,
            'grandtotal': grandtotal,
            'shipping'  : shipping
        }
        return render(request, 'cart_templates/cart.html', context)
    else:
        # Handle unauthenticated user case (redirect or display message)
        return redirect('userlogin')  # Example redirection
    # return render(request,'cart_templates/cart.html')


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
            

            # Calculate totals
            tax         = 0
            grandtotal  = 0
            total       = 0
            quantity    = 0
            cart_items  = CartItem.objects.filter(user=request.user)

            for cart_item1 in cart_items:
                total       += round(cart_item1.sub_total(), 2)
                quantity    += cart_item1.quantity
            shipping=100
            tax         = round(total / 100 * 5, 2)
            grandtotal  = round(tax + total + shipping, 2)

            context = {
                'total'     : total,
                'quantity'  : quantity,
                'cart_items': cart_items,
                'tax'       : tax,
                'grandtotal': grandtotal,
                
            }
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
    # Your existing code to calculate order summary
    total = 0
    quantity = 0
    shipping = 100

    # Calculate total, quantity, tax, and grandtotal
    for cart_item in CartItem.objects.filter(user=request.user):
        total += round(cart_item.sub_total(), 2)
        quantity += cart_item.quantity

    tax = round(total / 100 * 5, 2)
    grandtotal = round(tax + total + shipping, 2)
    # Return JSON response
    return JsonResponse({
        'total': total,
        'quantity': quantity,
        'shipping': shipping,
        'tax': tax,
        'grandtotal': grandtotal,
    })


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

