from django.shortcuts import reverse, HttpResponseRedirect

class RestrictMyAccountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/myaccount/') and (
            not hasattr(request.user, 'is_authenticated') or 
            not request.user.is_authenticated
        ):
            return HttpResponseRedirect(reverse('home'))  # Redirect to your home URL
        return self.get_response(request)
    
