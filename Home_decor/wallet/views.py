from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponseBadRequest
from .models import Wallet, Transaction,Account
from django.conf import settings
import json
import razorpay
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt, csrf_protect
# Create your views here.
#=================  WALLET ====================
def wallet(request):
    user = request.user
    wallet, created = Wallet.objects.get_or_create(user=user, defaults={'balance': 0})
    transactions = Transaction.objects.filter(wallet=wallet).all()
    print(wallet.balance,'Wallet balance')
    context = {'wallet': wallet, 'transactions': transactions}
    if request.method == 'POST':

        currency = 'INR'
        amount = int(json.loads(request.body)['amount']) 
        user = Account.objects.get(email=user.email)
        print(amount,user,currency)

        # Serialize user data and store in cache
        data = {'amount': amount}
        serialized_data = json.dumps(data)
        cache.set('payment_data', serialized_data)

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
        try:
            # Create Razorpay order
            print(settings.RAZOR_PAY_KEY_ID,settings.KEY_SECRET)
            data = {
                'amount':(int(amount)* 100),
                'currency':'INR',
            }
            payment1 = client.order.create(data=data)
            print(payment1)
            payment_order_id = payment1['id']
            context = {
                'amount': amount,
                'payment_order_id': payment_order_id,
                'RAZOR_PAY_KEY_ID': settings.RAZOR_PAY_KEY_ID,
            }

            return JsonResponse(context)
        except Exception as e:
            print('Error creating Razorpay order:', str(e))
            return JsonResponse({'error': 'Internal Server Error'}, status=500)
    # return render(request, 'account_templates/my-wallet.html', {'user': user})
    return render(request, 'account_templates/my-wallet.html', context)


@csrf_exempt
def paymenthandler2(request):
    print("Payment Handler endpoint reached")
    user = request.user
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
            print(result,'Hi not working?')
            if not result :
                # Payment signature verification failed
                return render(request, 'paymentfail.html')
                # return JsonResponse({'message': 'Payment signature verification failed'})
            else:
                amount = int(request.GET.get('amount'))
                user_id = request.GET.get('user_id')
                if amount:
                    user= Account.objects.get(id=user_id)
                    wallet=Wallet.objects.get(user=user)
                    wallet.balance+=amount
                    Transaction.objects.create(wallet=wallet, amount=amount, transaction_type='CREDIT')
                    wallet.save()
                    return redirect('wallet')  
                else:
                    return render(request, 'order_templates/paymentfail.html')
        except Exception as e:
            # Exception occurred during payment handling
            print('Exception:', str(e))
            # return HttpResponseBadRequest()
            return render(request, 'order_templates/paymentfail.html')

    else:
        # Redirect to login page if request method is not POST
        return redirect('shop')
    
