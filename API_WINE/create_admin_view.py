from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views import View

class CreateAdminView(View):
    def get(self, request):
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                email="admin@gmail.com",
                password="admin12345"  # Cambia esto a algo seguro luego
            )
            return JsonResponse({'message': 'Superusuario creado correctamente.'})
        else:
            return JsonResponse({'message': 'Ya existe un superusuario.'})