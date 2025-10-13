from django.db import models
from datetime import timedelta, date
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.exceptions import ValidationError

# Create your models here.
class Tipo_Producto(models.TextChoices):
    PORTATILES = 'portatil', 'Portatil'
    DESKTOP = 'desktop', 'Desktop'
    TABLET = 'tablet', 'Tablet'
    COMPONENTE = 'componente', 'Componente'
    ACCESORIO = 'accesorio', 'Accesorio'

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        db_table = 'categoria'

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=Tipo_Producto)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    stock = models.IntegerField(default=0)
    es_nuevo = models.BooleanField(default=False)
    es_mas_vendido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        db_table = 'producto'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre

class UserManager(BaseUserManager): # Clase para la creación de usuarios
    def create_user(self, correo, contraseña, **extra_fields): #extra_fields es un diccionario que puede contener cualquier campo adicional que se desee agregar al modelo de usuario
        if not correo:
            raise ValueError('El correo electrónico es obligatorio')
        usuario = self.model(correo=self.normalize_email(correo), **extra_fields) # Normaliza la dirección de correo electrónico convirtiendo todos los caracteres en minúsculas y eliminando cualquier espacio en blanco al principio o al final        
        usuario.set_password(contraseña) # Establece la contraseña del usuario encriptada 
        usuario.save()
        return usuario
    
class Usuario(AbstractBaseUser):
    correo = models.EmailField(unique=True)
    nombre = models.CharField(max_length=45)
    apellido = models.CharField(max_length=50)
    #user = models.CharField(max_length=30, unique=True)
    # foto_perfil = models.ImageField(upload_to='fotos/', null=True, blank=True, default='')
    
        
    OPCIONES_ROL = [
        ('recepcion', 'Recepcionista'),
        ('admin', 'Administrador')
    ]
    roles = models.CharField(max_length=10, choices=OPCIONES_ROL, default='recepcion')
    #password = models.CharField(max_length=300)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    #Usamos el UserManager personalizado
    objects = UserManager()

    #Se define el campo de autenticación sea el email
    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def get_full_name(self):
        return '{} {}'.format(self.nombre, self.apellido)

    def __str__(self):
        return self.get_full_name()
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuario'
        ordering = ['created_at']


