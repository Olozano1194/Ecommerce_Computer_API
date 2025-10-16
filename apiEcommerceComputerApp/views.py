from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Producto, Categoria, Usuario
from .serializers import (
    ProductoDetailSerializer, 
    ProductoListSerializer,
    CategoriaSerializer, 
    UsuarioSerializer,
    UsuarioRegistroSerializer,
    CambiarPasswordSerializer    
)
from .permissions import IsAdministrador

# Create your views here.
@extend_schema_view(
    list=extend_schema(
        description="Lista todos los productos o crea un nuevo producto"),
        retrieve=extend_schema(description="Obtiene los detalles de un producto específico por si ID"
    )
)

class ProductoViewSet(viewsets.ModelViewSet):
    """
   ViewSet para gestionar productos.
    - Lista: Todos pueden ver
    - Crear/Editar/Eliminar: Solo administradores
    """
    queryset = Producto.objects.all()
    permission_classes = [permissions.AllowAny]  # Lectura pública
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # filtros
    filterset_fields = {
        'categoria': ['exact'], 
        'tipo': ['exact'], 
        'precio': ['gte', 'lte'],
        'stock': ['gte', 'lte'],
    }
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['precio', 'fecha_creacion', 'nombre', 'cantidad_vendida']
    ordering = ['-fecha_creacion']

    def get_serializer_class(self):
        """
        Usa diferentes serializers según la acción.
        - List: ProductoListSerializer (ligero)
        - Retrieve: ProductoDetailSerializer (completo)
        """
        if self.action == 'list':
            return ProductoListSerializer
        return ProductoDetailSerializer

    def get_permissions(self):
        """
        Permisos personalizados según la acción.
        - Listar/Ver: Público
        - Crear/Editar/Eliminar: Solo admin
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Solo admin puede crear, actualizar o eliminar
            return [permissions.IsAuthenticated(), IsAdministrador()]
        return [permissions.AllowAny()]        
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def nuevos(self, request):
        """
        Endpoint: /productos/nuevos/
        Retorna productos nuevos (últimos 30 días)
        """
        productos_nuevos = Producto.objects.filter(es_nuevo=True)
        serializer = ProductoListSerializer(productos_nuevos, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])    
    def mas_vendidos(self, request):
        """
        Endpoint: /productos/mas_vendidos/
        Retorna los productos más vendidos (cantidad_vendida >= 10)
        """
        productos_vendidos = Producto.objects.filter(cantidad_vendida__gte=10).order_by('-cantidad_vendida')
        serializer = ProductoListSerializer(productos_vendidos, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def por_tipo(self, request):
        """
        Endpoint: /productos/por_tipo/?tipo=portatil
        Filtra productos por tipo (portatil, desktop, tablet, etc.)
        """
        tipo = request.query_params.get('tipo', None)
        
        if not tipo:
            return Response(
                {'error': 'Debes proporcionar el parámetro "tipo"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        productos = Producto.objects.filter(tipo=tipo)
        serializer = ProductoListSerializer(productos, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def agotados(self, request):
        """
        Endpoint: /productos/agotados/
        Retorna productos sin stock
        """
        productos_agotados = Producto.objects.filter(stock=0)
        serializer = ProductoListSerializer(productos_agotados, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def stock_bajo(self, request):
        """
        Endpoint: /productos/stock_bajo/
        Retorna productos con stock bajo (1-4 unidades)
        """
        productos_stock_bajo = Producto.objects.filter(stock__gt=0, stock__lt=5)
        serializer = ProductoListSerializer(productos_stock_bajo, many=True, context={'request': request})
        return Response(serializer.data)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        """
        ViewSet para gestionar categorías.
        - Lectura: Público
        - Escritura: Solo admin
        """
        queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    
    def get_permissions(self):
        """Permisos: lectura pública, escritura solo para admin"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdministrador()]
        return [permissions.AllowAny()]
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def productos(self, request, pk=None):
        """
        Endpoint: /categorias/{id}/productos/
        Retorna todos los productos de una categoría específica
        """
        categoria = self.get_object()
        productos = categoria.productos.all()
        serializer = ProductoListSerializer(productos, many=True, context={'request': request})
        return Response(serializer.data)

# Vistas específicas para la página principal
class ProductosNuevosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductoDetailSerializer
    permission_classes = [permissions.AllowAny] # Permitir acceso público
    
    def get_queryset(self):
        return Producto.objects.filter(es_nuevo=True)

class MasVendidosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductoDetailSerializer
    permission_classes = [permissions.AllowAny] # Permitir acceso público
    
    def get_queryset(self):
        return Producto.objects.filter(es_mas_vendido=True)

class ProductosPorTipoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductoDetailSerializer
    permission_classes = [permissions.AllowAny] # Permitir acceso público
    
    def get_queryset(self):
        tipo = self.kwargs['tipo']
        return Producto.objects.filter(tipo=tipo)
    
#esto nos sirve para que podamos crear el crud completo de los usuarios
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de usuarios.
    - Solo administradores pueden listar/ver todos los usuarios
    - Los usuarios pueden ver/editar su propio perfil
    """ 
    serializer_class = UsuarioSerializer
    queryset = Usuario.objects.all()
    permission_classes = [permissions.IsAuthenticated]  

    def get_permissions(self):
        """Permisos personalizados"""
        if self.action == 'create':
            # El registro se hace por otro endpoint
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """
        Usuarios normales solo ven su propio perfil.
        Admins ven todos.
        """
        user = self.request.user
        if user.is_staff or user.roles == 'admin':
            return Usuario.objects.all()
        return Usuario.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        Endpoint: /usuarios/me/
        Permite ver y editar el perfil del usuario actual
        """
        user = request.user
        
        if request.method == 'GET':
            serializer = UsuarioSerializer(user)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = UsuarioSerializer(user, data=request.data, partial=partial)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def cambiar_password(self, request):
        """
        Endpoint: /usuarios/cambiar_password/
        Permite cambiar la contraseña del usuario actual
        """
        serializer = CambiarPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'mensaje': 'Contraseña actualizada correctamente'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#esta es la autenticación del usuario osea me guarda el token donde debe ser
class RegistroUsuarioView(APIView):
    """
    Endpoint: POST /registro/
    Permite registrar nuevos usuarios como clientes.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UsuarioRegistroSerializer(data=request.data)
        
        if serializer.is_valid():
            usuario = serializer.save()
            
            # Obtiene el token creado automáticamente
            token = Token.objects.get(user=usuario)
            
            return Response({
                'mensaje': 'Usuario registrado exitosamente',
                'usuario': {
                    'id': usuario.id,
                    'correo': usuario.correo,
                    'nombre': usuario.nombre,
                    'apellido': usuario.apellido,
                    'roles': usuario.roles
                },
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#esta clase nos sirve para mostrar los datos del usuario
class userProfileView(APIView):
    """
    Endpoint: GET /perfil/
    Retorna los datos del usuario autenticado.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)    

# Login del usuario
class LoginView(APIView):
    """
    Endpoint: POST /login/
    Autentica usuarios y retorna un token.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        correo = request.data.get('correo')
        password = request.data.get('password')
        
        if not correo or not password:
            return Response(
                {'error': 'Correo y contraseña son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Autentica al usuario
        usuario = authenticate(request, username=correo, password=password)
        
        if usuario:
            # Obtiene o crea el token
            token, created = Token.objects.get_or_create(user=usuario)
            
            return Response({
                'token': token.key,
                'usuario': {
                    'id': usuario.id,
                    'correo': usuario.correo,
                    'nombre': usuario.nombre,
                    'apellido': usuario.apellido,
                    'nombre_completo': usuario.get_full_name(),
                    'roles': usuario.roles
                }
            }, status=status.HTTP_200_OK)
        
        return Response(
            {'error': 'Credenciales inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )

# Cerrar sesión
class LogoutView(APIView):
    """
    Endpoint: POST /logout/
    Elimina el token del usuario actual.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Elimina el token del usuario
            request.user.auth_token.delete()
            return Response(
                {'mensaje': 'Sesión cerrada correctamente'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )