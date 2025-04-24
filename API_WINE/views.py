from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomAuthTokenSerializer
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.utils.crypto import get_random_string
from .models import PasswordResetCode, User, Cliente, Manicurista, Servicio, Cita
from .serializers import (UserSerializer, ClienteSerializer, ManicuristaSerializer, ServicioSerializer, CitaSerializer, PasswordResetRequestSerializer, PasswordResetVerifySerializer)
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()

def home(request):
    return JsonResponse({'mensaje': 'API WINE SPA funciona correctamente '})

# Vistas para User
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Cliente
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

# Manicurista
class ManicuristaViewSet(viewsets.ModelViewSet):
    queryset = Manicurista.objects.all()
    serializer_class = ManicuristaSerializer

# Servicio
class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

# Cita
class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.all()
    serializer_class = CitaSerializer

    def perform_create(self, serializer):
        cliente = serializer.validated_data['cliente']
        manicurista = serializer.validated_data['manicurista']
        fecha = serializer.validated_data['fecha']
        hora_inicio = serializer.validated_data['hora_inicio']
        hora_fin = serializer.validated_data['hora_fin']

        citas_existentes = Cita.objects.filter(
            (Q(cliente=cliente) | Q(manicurista=manicurista)),
            fecha=fecha
        )

        for cita in citas_existentes:
            if (hora_inicio >= cita.hora_inicio and hora_inicio < cita.hora_fin) or \
               (hora_fin > cita.hora_inicio and hora_fin <= cita.hora_fin):
                raise ValidationError("Ya existe una cita en el horario solicitado.")

        serializer.save()

    def perform_update(self, serializer):
        cita = self.get_object()
        if cita.estado == 'finalizada':
            raise ValidationError("No se puede modificar una cita finalizada.")

        serializer.save()
     
class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'Este correo no está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

            # Generar código
            code = get_random_string(length=6, allowed_chars='0123456789')

            # Borrar códigos anteriores y guardar nuevo
            PasswordResetCode.objects.filter(email=email).delete()
            PasswordResetCode.objects.create(email=email, code=code)

            # Enviar correo
            send_mail(
                'Código de recuperación de contraseña',
                f'Tu código de recuperación es: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )

            return Response({'message': 'Se ha enviado un código de recuperación a tu correo.'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PasswordResetVerifyView(APIView):
    def post(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']

            try:
                PasswordResetCode.objects.filter(
                    email=email, 
                    created_at__lt=timezone.now() - timedelta(minutes=10)
                ).delete()
                # Verifica si el código es válido
                reset_code = PasswordResetCode.objects.get(email=email, code=code)

                if reset_code.is_expired():
                    return Response({"detail": "El código ha expirado"}, status=status.HTTP_400_BAD_REQUEST)

                # Cambia la contraseña del usuario
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()

                # Borra el código de la base de datos
                reset_code.delete()

                return Response({"detail": "Contraseña actualizada con éxito"}, status=status.HTTP_200_OK)

            except PasswordResetCode.DoesNotExist:
                return Response({"detail": "Código incorrecto o no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

            except User.DoesNotExist:
                return Response({"detail": "Usuario no encontrado"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CustomTokenObtainPairView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CustomAuthTokenSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Autenticamos al usuario directamente
            user = authenticate(username=email, password=password)
            if user is None:
                return Response({'detail': 'Correo electrónico o contraseña incorrectos.'}, status=status.HTTP_401_UNAUTHORIZED)

            # Generamos el token JWT
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)