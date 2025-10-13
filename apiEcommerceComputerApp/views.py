from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Producto, Categoria
from .serializers import ProductoSerializer, CategoriaSerializer

# Create your views here.
@extend_schema_view(
    list=extend_schema(
        description="Lista todos los productos o crea un nuevo producto"),
        retrieve=extend_schema(description="Obtiene los detalles de un producto específico por si ID"
    )
)
class ProductoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar productos."""
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'tipo', 'es_nuevo', 'es_mas_vendido']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['precio', 'fecha_creacion']

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

# Vistas específicas para la página principal
class ProductosNuevosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductoSerializer
    
    def get_queryset(self):
        return Producto.objects.filter(es_nuevo=True)

class MasVendidosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductoSerializer
    
    def get_queryset(self):
        return Producto.objects.filter(es_mas_vendido=True)

class ProductosPorTipoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductoSerializer
    
    def get_queryset(self):
        tipo = self.kwargs['tipo']
        return Producto.objects.filter(tipo=tipo)