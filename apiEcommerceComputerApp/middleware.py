from django.http import Http404
from django.urls import reverse

class RestrictAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(reverse('admin:index')):
            if not request.user.is_authenticated or not request.user.is_superuser:
                raise Http404 # 🔥 Devuelve un 404 en lugar de la página de login
        return self.get_response(request)