from django.contrib import admin
from .models import Usuario, Producto, Categoria

# Register your models here.
# Registro sencillo para Categoria
admin.site.register(Categoria)

# Registro personalizado para Usuario, para ver más campos en la lista
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('correo', 'nombre', 'apellido', 'roles', 'is_staff') # Muestra estos campos en la lista
    list_filter = ('roles', 'is_staff') # Añade filtros en la barra lateral

admin.site.register(Usuario, UsuarioAdmin)

# Registro personalizado para Producto
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'categoria', 'tipo', 'es_nuevo')
    list_filter = ('categoria', 'tipo', 'es_nuevo')
    search_fields = ('nombre',) # Añade un buscador por nombre

admin.site.register(Producto, ProductoAdmin)
