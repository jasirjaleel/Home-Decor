from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from user_app.models import Account
from account.models import Address
from .models import *
from django.http import JsonResponse
import json
from order.models import OrderProduct, Order
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from wallet.models import Wallet, Transaction
from product_management.models import Product
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Prefetch
import csv
from django.http import HttpResponse
import xlwt
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO



def admin_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        if user is not None and user.is_superadmin == True:
            login(request, user)
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                messages.success(request, 'Successfuly Logged in')
                return redirect('adminhome')
        else:
            messages.error(request, 'Bad Credentials!')
            return render(request, 'admin_templates/admin-login.html')
    return render(request, 'admin_templates/admin-login.html')

@never_cache
@login_required(login_url='admin_login')
def adminhome(request):
    orders = Order.objects.filter(is_ordered=True)
    order_count = orders.count()
    order_total = orders.aggregate(total_order_amount=Sum('order_total'))
    order_total_amount = float(order_total['total_order_amount'])
    products = Product.objects.filter(
        is_available=True).select_related('category')
    product_count = products.count()
    category_count = products.values(
        'category__category_name').distinct().count()
    context = {
        'order_count': order_count,
        'product_count': product_count,
        'category_count': category_count,
        'order_total': order_total_amount,
    }
    return render(request, "admin_templates/index.html", context)


@never_cache
@login_required(login_url='admin_login')
def adminlogout(request):
    logout(request)
    messages.success(request, 'Successfuly Logged Out')
    return redirect('home')


@never_cache
@login_required(login_url='admin_login')
def all_users(request):
    if request.user.is_superadmin:
        # if request.method == 'POST':
        #         search_word = request.POST.get('search-box', '')
        #         data = User.objects.filter(Q(username__icontains=search_word)| Q(email__icontains=search_word)).order_by('id').values()
        #     else:
        data = Account.objects.all().order_by('id').exclude(is_superadmin=True)
        paginator = Paginator(data, 5)
        page = request.GET.get('page')
        paged_users = paginator.get_page(page)
        context = {'users': paged_users}
        return render(request, "admin_templates/all_users.html", context=context)
    return redirect('usersignup')


def blockuser(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_user_id = data.get('userId')
        print(selected_user_id)
        if selected_user_id:
            try:
                user = Account.objects.get(id=selected_user_id)
                if user.is_blocked:
                    # User is currently blocked, so unblock
                    user.is_blocked = False
                    user.save()
                    message = 'User unblocked successfully'
                else:
                    user.is_blocked = True
                    user.save()
                    message = 'User blocked successfully'
                return JsonResponse({'success': True, 'message': message})
            except Account.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found'})
        else:
            return JsonResponse({'success': False, 'message': 'No user ID provided'})
    return render(request, "admin_templates/usermanagement.html", {})

@login_required(login_url='admin_login')
def user_details(request):
    user_id = request.GET.get('user_id')
    user = Account.objects.get(id=user_id)
    wallet = Wallet.objects.filter(user=user).first()
    address = Address.objects.filter(account=user.id, is_default=True).first()
    ordered_products = OrderProduct.objects.filter(
        user=user, ordered=True).order_by('-id')
    context = {
        "user": user,
        'address': address,
        'ordered_products': ordered_products,
        'ordered_products_count': ordered_products.count(),
        'wallet': wallet,
    }
    return render(request, 'admin_templates/user_details.html', context)
##################### CHANGE ORDER STATUS OF PRODUCT ########################


def update_order_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            new_status = data.get('new_status')
            print(order_id, new_status)
            order = Order.objects.get(id=order_id)
            order.order_status = new_status
            order.save()
            return JsonResponse({'message': 'Order status updated successfully'}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


########################## CHART #################################
def fetch_monthly_data(request):
    response = {}
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    current_date = start_date
    while current_date < end_date:
        next_date = current_date + timedelta(days=1)
        purchase_count = Order.objects.filter(
            created_at__gte=current_date, created_at__lt=next_date, is_ordered=True).count()
        response[current_date.day] = purchase_count
        current_date = next_date
    return JsonResponse({'response': response}, status=200)


def fetch_weekly_data(request):
    response = {}
    end_date = timezone.now()
    start_date = end_date - timedelta(days=6)
    current_date = start_date
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        purchase_count = Order.objects.filter(
            created_at__date=current_date, is_ordered=True).count()
        day_name = current_date.strftime("%A")
        response[day_name] = purchase_count
        current_date = next_date
    return JsonResponse({'response': response}, status=200)


def fetch_yearly_data(request):
    response = {}
    end_date = timezone.now()
    start_date = end_date.replace(month=1, day=1)
    current_date = start_date
    while current_date <= end_date:
        next_month = current_date.replace(month=(current_date.month + 1))
        purchase_count = Order.objects.filter(
            created_at__gte=current_date, created_at__lt=next_month, is_ordered=True
        ).count()
        month_name = current_date.strftime("%B")
        response[month_name] = purchase_count
        current_date = next_month
    return JsonResponse({'response': response}, status=200)


def fetch_custom_data(request):
    response = {}
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%d-%m-%Y').date()
        end_date = datetime.strptime(end_date, '%d-%m-%Y').date()
        current_date = start_date
        while current_date <= end_date:
            purchase_count = Order.objects.filter(
                created_at__date=current_date, is_ordered=True).count()
            response[str(current_date)] = purchase_count
            current_date += timedelta(days=1)
    return JsonResponse({'response': response}, status=200)



######################### Transcations ############################
@never_cache
@login_required(login_url='admin_login')
def transactions(request):
    transactions = Transaction.objects.all()
    paginator = Paginator(transactions, 10)
    page = request.GET.get('page')
    paged_transactions = paginator.get_page(page)
    context = {
        'transactions': paged_transactions,
    }
    return render(request, 'admin_templates/transactions.html', context)

################### sales report ############################
@never_cache
@login_required(login_url='admin_login')
def sales_report(request):
    orders = Order.objects.prefetch_related(
        Prefetch('order_products', queryset=OrderProduct.objects.all())
    ).all().order_by('id')
    paginator = Paginator(orders, 20)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    context = {
        'orders': paged_orders,
    }
    return render(request, 'admin_templates/sales_report.html', context)

########################### DOWNLOAD ############################
import os 
# from weasyprint import HTML

def download_pdf(request):
    current_date = datetime.now().strftime("%d-%m-%Y")
    filename = f"sales_report_{current_date}.pdf"
    html_string = render_to_string('admin_templates/pdf-output.html', {'orders': Order.objects.all()})
    os.add_dll_directory(r'C:\msys64\mingw64\bin')
    # html = HTML(string=html_string)
    html = 'hi'
    pdf_file = html.write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def download_excel(request):
    try:
        response = HttpResponse(content_type='applications/ms-excel')
        current_date = datetime.now().strftime("%d-%m-%Y")
        filename = f"sales_report_{current_date}.xls"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Sales Report')
        row_num = 0
        font_style = xlwt.XFStyle()
        columns = ['Date', 'Order ID', 'Billing Name', 'Wallet Discount', 'Shipping Charge', 'Offer', 'Additional Discount', 'Tax', 'Total']
        
        for col_num, column_title in enumerate(columns):
            ws.write(row_num, col_num, column_title, font_style)

        for order in Order.objects.all().order_by('id'):
            try:
                row_num += 1
                ws.write(row_num, 0, order.created_at.strftime('%d %b %Y'))
                ws.write(row_num, 1, order.order_number[12:])
                ws.write(row_num, 2, order.shipping_address.first_name if order.shipping_address else '')
                ws.write(row_num, 3, order.wallet_discount)
                ws.write(row_num, 4, order.shipping_charge)
                ws.write(row_num, 5, order.offer)
                ws.write(row_num, 6, order.additional_discount)
                ws.write(row_num, 7, order.order_tax)
                ws.write(row_num, 8, order.order_total)
            except Exception as e:
                messages.error(request, f'Error: {e}')
                return redirect('sales_report')
        wb.save(response)
        return response
    except Exception as e:
        messages.error(request, f'Error: {e}')
        return redirect('sales_report')
    
def download_csv(request):
    try:
        response = HttpResponse(content_type='text/csv')
        current_date = datetime.now().strftime("%d-%m-%Y")
        filename = f"sales_report_{current_date}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Order ID', 'Billing Name', 'Wallet Discount', 'Shipping Charge', 'Offer', 'Additional Discount', 'Tax', 'Total'])

        for order in Order.objects.all().order_by('id'):
            writer.writerow([
                order.created_at.strftime('%d %b %Y'),
                order.order_number[12:],
                order.shipping_address.first_name,
                order.wallet_discount,
                order.shipping_charge,
                order.offer,
                order.additional_discount,
                order.order_tax,
                order.order_total
            ])

        return response
    except Exception as e:
        messages.error(request, f"Error downloading CSV: {str(e)}")
        return redirect('sales_report')
