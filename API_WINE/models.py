from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import datetime
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver



# Create your models here.
# validar la fecha de finalización no sea mayor a 30 días
def validate_fecha_finalizacion(value):
    fecha_actual = timezone.now().date()
    fecha_minima = fecha_actual + datetime.timedelta(days=30)

    if value < fecha_minima:
        raise ValidationError(
            f"La fecha de finalización debe ser al menos un mes después de hoy (fecha mínima permitida: {fecha_minima})."
        )
        
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    celular = models.CharField(max_length=15)
    estado = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['celular']

    objects = UserManager()

    def __str__(self):
        return self.email
    
class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cliente: {self.usuario.email}"

class Manicurista(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Manicurista: {self.usuario.email}"
    
class Novedad(models.Model):
    cita = models.OneToOneField('Cita', on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Novedad de la cita {self.cita.id}"
    
class Servicio(models.Model):
    nombre = models.CharField(max_length=45)
    precio = models.FloatField(validators=[MinValueValidator(0.0)])
    descripcion = models.TextField()
    estado = models.BooleanField(default=True)  # True = activo, False = inactivo

    def __str__(self):
        return self.nombre
    
class Cita(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    manicurista = models.ForeignKey('Manicurista', on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('confirmada', 'Confirmada'),
            ('cancelada', 'Cancelada'),
            ('finalizada', 'Finalizada')
        ],
        default='pendiente'
    )

    def __str__(self):
        return f"Cita {self.id} - {self.fecha} - {self.estado}"
    
# recuperar contraseña
class PasswordResetCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)  # código válido por 10 min

    def __str__(self):
        return f"{self.email} - {self.code}"
    
@receiver(post_save, sender=Cita)
def crear_novedad_al_finalizar_cita(sender, instance, **kwargs):
    if instance.estado == 'finalizada' and not hasattr(instance, 'novedad'):
        Novedad.objects.create(cita=instance)