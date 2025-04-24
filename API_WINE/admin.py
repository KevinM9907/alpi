from django.contrib import admin
from .models import User, Cliente, Manicurista, Servicio, Cita,PasswordResetCode

# Registra el modelo User
admin.site.register(User)

# Registra Cliente y Manicurista (no necesitan un modelo extra si solo tienen el campo de usuario)
admin.site.register(Cliente)
admin.site.register(Manicurista)

# Registra el modelo Servicio
admin.site.register(Servicio)

# Registra el modelo Cita
@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'manicurista', 'servicio', 'fecha', 'hora_inicio', 'hora_fin', 'estado')
    list_filter = ('estado', 'fecha', 'manicurista')
    search_fields = ('cliente__usuario__email', 'manicurista__usuario__email', 'servicio__nombre')

# Registra el modelo PasswordResetCode
@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'created_at')
    search_fields = ('email',)
