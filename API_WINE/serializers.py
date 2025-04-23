from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Cliente, Manicurista, Novedad, Servicio, Cita, PasswordResetCode
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'celular', 'estado']
        
class ClienteSerializer(serializers.ModelSerializer):
    usuario = UserSerializer()

    class Meta:
        model = Cliente
        fields = ['id', 'usuario']

class ManicuristaSerializer(serializers.ModelSerializer):
    usuario = UserSerializer()

    class Meta:
        model = Manicurista
        fields = ['id', 'usuario']
        
class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'precio', 'descripcion', 'estado']


class CitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = [
            'id', 'cliente', 'manicurista', 'servicio',
            'fecha', 'hora_inicio', 'hora_fin', 'estado'
        ]

    def validate(self, data):
        if data['hora_inicio'] >= data['hora_fin']:
            raise serializers.ValidationError("La hora de inicio debe ser antes que la hora de fin.")
        return data
    
class NovedadSerializer(serializers.ModelSerializer):
    cita = CitaSerializer(read_only=True)

    class Meta:
        model = Novedad
        fields = ['id', 'cita', 'observaciones', 'fecha_registro']
        
        
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)
    
class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email is None or password is None:
            raise serializers.ValidationError('Debe proporcionar tanto el correo como la contraseña.')

        # Usamos el email como 'username' en el proceso de autenticación
        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError('Correo electrónico o contraseña incorrectos.')

        if not user.is_active:
            raise serializers.ValidationError('El usuario está inactivo.')

        # Crear un token JWT
        refresh = RefreshToken.for_user(user)
        
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'email': user.email,
            'is_active': user.is_active,
        }
        