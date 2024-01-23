from django.shortcuts import render,redirect
from .models import CartItem
from django.contrib import messages
from django.http import JsonResponse
from admin_app.models import Product
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
# Create your views here.
@never_cache
def cart(request):
    total = 0
    quantity = 0
    cart_items = None

    if request.user.is_authenticated:
        tax = 0
        grandtotal = 0
        cart_items = CartItem.objects.filter( currentuser=request.user)

        if not cart_items.exists():  # Check if the cart is empty
            return render(request, 'cart_templates/empty-cart.html')  #

        for cart_item in cart_items:
            total += round((cart_item.product.price * cart_item.quantity), 2)
            quantity += cart_item.quantity

        tax = round(total / 100 * 15, 2)
        grandtotal = round(tax + total, 2)

        context = {
            'total': total,
            'quantity': quantity,
            'cart_items': cart_items,
            'tax': tax,
            'grandtotal': grandtotal
        }
        print('hi2')
        return render(request, 'cart_templates/cart.html', context)
    else:
        # Handle unauthenticated user case (redirect or display message)
        return redirect('userlogin')  # Example redirection
    # return render(request,'cart_templates/cart.html')


@never_cache
def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        try:
            product = Product.objects.get(id=product_id)
            if product.is_available:
                try:
                    cart_item = CartItem.objects.get(currentuser=request.user, product=product)
                    # cart_item.quantity += 1
                    if cart_item.product.stock < cart_item.quantity:
                        messages.error(request, 'Out of Stock')
                    else:
                        cart_item.save()

                except CartItem.DoesNotExist:
                    cart_item = CartItem.objects.create(
                        product=product,
                        quantity=1,
                        currentuser=request.user,
                    )
                    cart_item.save()

                # Calculate totals
                tax = 0
                grandtotal = 0
                total = 0
                quantity = 0
                cart_items = CartItem.objects.filter(currentuser=request.user)

                for cart_item1 in cart_items:
                    total += round((cart_item1.product.price * cart_item1.quantity), 2)
                    quantity += cart_item1.quantity

                tax = round(total / 100 * 5, 2)
                grandtotal = round(tax + total, 2)

                context = {
                    'total': total,
                    'quantity': quantity,
                    'cart_items': cart_items,
                    'tax': tax,
                    'grandtotal': grandtotal
                }
                print('hi')
                messages.success(request, "Item added to cart")
                # return render(request, 'cart_templates/cart.html', context)
                return redirect('cart')

            else:
                messages.success(request, 'Product is currently unavailable')
                return redirect('shop')

        except Product.DoesNotExist:
            messages.error(request, 'Product does not exist')
            return redirect('shop')

    else:
        messages.error(request, 'You should sign in first to add an item to your cart')
        return redirect('userlogin')


@never_cache
def update_cart(request, cart_item_id, new_quantity):
    cart_item = CartItem.objects.get(id=cart_item_id)

    try:
        new_quantity = int(new_quantity)
    except ValueError:
        response_data = {
            'success': False,
            'message': 'Invalid quantity format',
        }
        return JsonResponse(response_data)

    if new_quantity > 0:
        cart_item.quantity = new_quantity
        cart_item.save()

        response_data = {
            'success': True,
            'subtotal': cart_item.sub_total(),
        }
    else:
        response_data = {
            'success': False,
            'message': 'Invalid quantity',
        }

    return JsonResponse(response_data)


@login_required
def delete_cart_item(request, cart_item_id):
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, currentuser=request.user)
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


def get_cart_total(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(currentuser=request.user)
        total = sum(cart_item.sub_total() for cart_item in cart_items)
        return JsonResponse({'total': total})
    else:
        return JsonResponse({'total': 0})
    

def payment(request):
    return render(request,'cart_templates/payment.html')