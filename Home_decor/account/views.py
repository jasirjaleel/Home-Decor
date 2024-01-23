from django.shortcuts import render

# Create your views here.

def my_account(request):
    return render(request,'account_templates/my-account.html')

def my_address(request):
    return render(request,'account_templates/my-address.html')


def add_address(request):
    return render(request,'account_templates/add-address.html')

def my_order(request):
    return render(request,'account_templates/orders.html')

def my_profile(request):
    return render(request,'account_templates/my-profile.html')