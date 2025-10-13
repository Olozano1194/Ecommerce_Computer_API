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
        db_table = 'dbecommercecomputer'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre

class UserManager(BaseUserManager): # Clase para la creación de usuarios
    def create_user(self, email, password, **extra_fields): #extra_fields es un diccionario que puede contener cualquier campo adicional que se desee agregar al modelo de usuario
        if not email:
            raise ValueError('Los usuarios deben tener un correo electrónico')
        user = self.model(email=self.normalize_email(email), **extra_fields) # Normaliza la dirección de correo electrónico convirtiendo todos los caracteres en minúsculas y eliminando cualquier espacio en blanco al principio o al final        
        user.set_password(password) # Establece la contraseña del usuario encriptada 
        user.save()
        return user
    
class Usuario(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=45)
    lastname = models.CharField(max_length=50)
    #user = models.CharField(max_length=30, unique=True)
    avatar = models.ImageField(upload_to='fotos/', null=True, blank=True, default='')
    
        
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
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'lastname']

    def full_name(self):
        return '{} {}'.format(self.name, self.lastname)

    def __str__(self):
        return self.full_name()
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuario'
        ordering = ['created_at']


