from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect

# Middleware to block normal users from accessing the Django admin interface
# Redirects non-admin users to the home page
class RestrictAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and (not hasattr(request.user, 'is_authenticated') or not request.user.is_authenticated or not request.user.is_superadmin) and request.path != '/admin/login/' :
            return redirect('home') 
        return self.get_response(request)