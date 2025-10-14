from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Producto, Categoria, Usuario
from .serializers import ProductoSerializer, CategoriaSerializer, UsuarioSerializer
from .permissions import IsAdministrador, ReadOnlyOrAdmin

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
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'tipo', 'es_nuevo', 'es_mas_vendido']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['precio', 'fecha_creacion', 'nombre']
    ordering = ['-fecha_creacion']

    def get_permissions(self):
        """
        Asignar los permisos según la acción.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Solo admin puede crear, actualizar o eliminar
            return [IsAdministrador()]
        else:
            # Cualquiera puede ver (Get, List)
            return [permissions.AllowAny()]
    
    def get_queryset(self):
        """
        Filtrar productos según el rol del usuario.
        """
        queryset = Producto.objects.all()
        # si el usuario es admin, ve todos los productos
        if self.request.user.is_authenticated and self.request.user.roles == 'admin':
            return queryset
        
        # Usuarios normales solo ven productos activos
        return queryset
    
    def perform_create(self, serializer):
        """
        Asignar automaticamente el suaurio actual al crear un producto.
        """
        serializer.save(creado_por=self.request.user)
    
    @action(detail=False, methods=['get'])
    def mis_productos(self, request):
        """
        Endpoint personalizado para que los admin vean sus productos creados.
        """
        if not request.user.is_authenticated or request.user.roles != 'admin':
            return Response(
                {'error': 'No tienes permisos para ver esta información.'},
                status=status.HTTP_403_FORBIDDEN
            )
    
        productos = Producto.objects.filter(creado_por=request.user)
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        """
        Permisos para categorías: lectura pública, escritura solo para admin.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdministrador()]
        else:
            return [permissions.AllowAny()]

# Vistas específicas para la página principal
class ProductosNuevosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny] # Permitir acceso público
    
    def get_queryset(self):
        return Producto.objects.filter(es_nuevo=True)

class MasVendidosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny] # Permitir acceso público
    
    def get_queryset(self):
        return Producto.objects.filter(es_mas_vendido=True)

class ProductosPorTipoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny] # Permitir acceso público
    
    def get_queryset(self):
        tipo = self.kwargs['tipo']
        return Producto.objects.filter(tipo=tipo)
    
#esto nos sirve para que podamos crear el crud completo de los usuarios
class UserViewSet(viewsets.ModelViewSet): 
    serializer_class = UsuarioSerializer
    queryset = get_user_model().objects.all()
    # parser_classes = (MultiPartParser, FormParser)   

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Errores de validación:", serializer.errors)
            return Response({
                "error": "Datos inválidos",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        #Guardamos el usuario
        user_data = serializer.save()
        #Generamos el token
        token, created = Token.objects.get_or_create(user=user_data)

        return Response({
            "user": UsuarioSerializer(user_data).data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)
    
    # def update(self, request, *args, **kwargs):
    #     try:
    #         partial = kwargs.pop('partial', False)
    #         instance = self.get_object()

    #         # print("Datos antes de la validación:", request.data)

    #         # Se guarda la imagen anterior por si acaso
    #         old_avatar = instance.avatar if instance.avatar else None

    #         serializer = self.get_serializer(
    #             instance, 
    #             data=request.data, 
    #             partial=partial,
    #             context={'request': request}
    #         )

    #         if serializer.is_valid():
    #             # print("Datos válidos, procediendo con la actualización.")

    #             # Si hay avatar en los archivos, lo agregamos a los datos
    #             if 'avatar' in request.FILES:
    #                 if old_avatar:
    #                     instance.avatar.delete(save=False)
    #                 instance.avatar = request.FILES['avatar']

    #             updated_instance = serializer.save()
    #             return Response(serializer.data, status=status.HTTP_200_OK)
            
    #         else:
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #              # Verificar que la actualización fue exitosa
    #             #if updated_instance:
    #                 # print("Actualización exitosa")
    #                 #return Response(
    #                     #serializer.data,
    #                     #status=status.HTTP_200_OK
    #                 #)
    #         #     else:
    #         #         # print("Error: La actualización no devolvió una instancia")
    #         #         # Si algo salió mal, devolvemos la imagen anterior
    #         #         if old_avatar:
    #         #             instance.avatar = old_avatar
    #         #             instance.save()
    #         #         return Response(
    #         #             {"error": "Error al actualizar el usuario"},
    #         #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         #         )
    #         # else:
    #         #     # print("Errores de validación:", serializer.errors)
    #         #     return Response(
    #         #         serializer.errors,
    #         #         status=status.HTTP_400_BAD_REQUEST
    #         #     )

    #     except Exception as e:
    #         print("Error inesperado:", str(e))
    #         return Response({"error": "Error inesperado"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#esta es la autenticación del usuario osea me guarda el token donde debe ser
class CustomAuthTokenViewSet(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('correo')
        password = request.data.get('contraseña')

        if not email or not password:
            return Response({'error': 'Correo y contraseña son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        #autenticamos el usuario
        user = authenticate(request, username=email, password=password)
        #si el usuario es correcto generamos el token
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Credenciales invalidas'}, status=status.HTTP_400_BAD_REQUEST)

#esta clase nos sirve para mostrar los datos del usuario y poder hacer el login respectivo
class userProfileView(APIView):
    permission_classes = [IsAuthenticated]
    #parser_classes = (MultiPartParser, FormParser) #para poder subir archivos

    def get(self, request):
        try:
            user_serializer = UsuarioSerializer(request.user, context={'request': request})
            user_data = user_serializer.data            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'user': user_data}, status=status.HTTP_200_OK)
         
    #esta clase nos sirve para listar los usuarios
    def list(self,request):
        try:
           users = Usuario.objects.all().order_by('-id')
           serializer = UsuarioSerializer(users, many=True, context={'request': request})
           return Response({'users': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
           return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)    
        