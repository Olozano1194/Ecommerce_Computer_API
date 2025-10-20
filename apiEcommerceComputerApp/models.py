from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError

# Create your models here.
class UserManager(BaseUserManager): 
    """ 
    Clase para la creación de usuarios personalizados con correo electrónico como identificador único.
    """
    def create_user(self, email, password=None, **extra_fields): #extra_fields es un diccionario que puede contener cualquier campo adicional que se desee agregar al modelo de usuario
        """
        Crea y guarda un usuario regular con el correo y contraseña datos.
        """
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        usuario = self.model(email=self.normalize_email(email), **extra_fields) # Normaliza la dirección de correo electrónico convirtiendo todos los caracteres en minúsculas y eliminando cualquier espacio en blanco al principio o al final               
        usuario.set_password(password) # Establece la contraseña del usuario encriptada 
        usuario.save(using=self._db) # Guarda el usuario en la base de datos
        return usuario
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crea y guarda un superusuario con privilegios de staff.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Roles(models.TextChoices):
    """
     Roles disponibles para los usuarios.
    """
    ADMIN = 'admin', 'Administrador'
    CLIENTE = 'cliente', 'Cliente'
    # PROVEEDOR = 'proveedor', 'Proveedor'

class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo personalizado de usuario que utiliza el correo electrónico como identificador único.
    """
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=45)
    apellido = models.CharField(max_length=50)         
    
    roles = models.CharField(max_length=10, choices=Roles.choices, default='CLIENTE')    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    #Usamos el UserManager personalizado
    objects = UserManager()

    #Se define el campo de autenticación sea el email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def get_full_name(self):
        """
        Retorna el nombre completo del usuario.
        """
        return '{} {}'.format(self.nombre, self.apellido)

    def __str__(self):
        return self.get_full_name()
    
    def has_perm(self, perm, obj=None):
        """
        Verifica si el usuario tiene permisos para ver o editar la información.
        """
        return self.is_superuser 

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuario'
        ordering = ['-created_at']

class Categoria(models.Model):
    """
    Categorás de productos.
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        db_table = 'categoria'

    def __str__(self):
        return self.nombre

class Tipo_Producto(models.TextChoices):
    """
    Tipos de productos disponibles.
    """
    PORTATILES = 'portatil', 'Portátil'
    DESKTOP = 'desktop', 'Desktop'
    TABLET = 'tablet', 'Tablet'
    COMPONENTE = 'componente', 'Componente'
    ACCESORIO = 'accesorio', 'Accesorio'

class Producto(models.Model):
    """
    Modelo principal para los productos del ecommerce.
    """
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    tipo = models.CharField(max_length=20, choices=Tipo_Producto.choices)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    stock = models.IntegerField(default=0)
    # Campos de control de ventas
    cantidad_vendida = models.IntegerField(default=0)
    es_nuevo = models.BooleanField(default=False)
    # Campos de fecha
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='productos_creados',
        null=True,
        blank=True
    )

    def clean(self):
        """
        Validaciones personalizadas para el modelo Producto.
        """
        if self.precio < 0:
            raise ValidationError({'precio': 'El precio no puede ser negativo.'})
        if self.stock < 0:
            raise ValidationError({'stock': 'El stock no puede ser negativo.'})

    def save(self, *args, **kwargs):
        """
        Override del método save para calcular si el producto es nuevo.
        """
        # Calcula si el producto es nuevo (creado en los últimos 30 días)
        if self.pk is None:
            self.es_nuevo = True
        else:
            fecha_limite = timezone.now() - timedelta(days=30)
            self.es_nuevo = self.fecha_creacion >= fecha_limite

        super().save(*args, **kwargs)
    
    @property
    def es_mas_vendido(self):
        """
        Determina si es más vendido basándose en la cantidad vendida.
        Se considera más vendido si tiene más de 10 ventas.
        """
        return self.cantidad_vendida >= 10
    
    @property
    def esta_agotado(self):
        """
        Verifica si el producto está agotado.
        """
        return self.stock == 0
    
    @property
    def stock_bajo(self):
        """
        Verifica si el stock está bajo (menos de 5 unidades).
        """
        return 0 < self.stock < 5
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        db_table = 'producto'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['tipo', 'categoria']),
            models.Index(fields=['-cantidad_vendida']),
            models.Index(fields=['-fecha_creacion']),
        ]

class ImagenProducto(models.Model):
    """
    Imágenes adicionales para cada producto.
    """
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE,
        related_name='imagenes_adicionales'
    )
    imagen = models.ImageField(upload_to='productos/adicionales/')
    orden = models.PositiveIntegerField(default=0)  # Para ordenar las imágenes
    es_principal = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Imagen {self.orden} de {self.producto.nombre}'
    
    class Meta:
        verbose_name = 'Imagen del Producto'
        verbose_name_plural = 'Imágenes de Productos'
        db_table = 'imagen_producto'
        ordering = ['producto', 'orden']
        unique_together = [['producto', 'orden']]
