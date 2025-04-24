from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from django.http import HttpResponse
from .create_admin_view import CreateAdminView
from .views import (
    UserViewSet,
    ClienteViewSet,
    ManicuristaViewSet,
    ServicioViewSet,
    PasswordResetVerifyView,
    CitaViewSet,
    PasswordResetVerifyView, PasswordResetRequestView
)

def login_welcome(request):
    return HttpResponse("Bienvenido a WINE SPA. Accede con tus credenciales.")

# Creamos un router para las vistas de API que usan ModelViewSet
router = DefaultRouter()

# Registro de las vistas ModelViewSet con un basename único
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'manicuristas', ManicuristaViewSet, basename='manicurista')
router.register(r'servicios', ServicioViewSet, basename='servicio')
router.register(r'citas', CitaViewSet, basename='cita')

urlpatterns = [
    path('', include(router.urls)),  # Rutas de la API
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'), # La vista personalizada para la página de login
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Aquí puedes gestionar el login JWT
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/verify/', PasswordResetVerifyView.as_view(), name='password-reset-verify'),path('crear-admin/', CreateAdminView.as_view(), name='crear-admin'),
]
