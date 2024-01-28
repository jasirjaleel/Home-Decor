from django.http import HttpResponseRedirect
from django.urls import reverse

# Middleware to block normal users from accessing the Django admin interface
# Redirects non-admin users to the home page
class RestrictAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and hasattr(request.user, 'is_authenticated') and request.user.is_authenticated and not request.user.is_superadmin:
            return HttpResponseRedirect(reverse('home'))  # Redirect to your home URL
        return self.get_response(request)