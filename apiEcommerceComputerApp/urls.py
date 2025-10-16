from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import(
    ProductoViewSet, 
    CategoriaViewSet,
    RegistroUsuarioView,
    LoginView,
    LogoutView, 
    UserViewSet,
    userProfileView
)

#api versioning
router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'usuarios', UserViewSet, basename='usuario')


urlpatterns = [
    # ===== ROUTER (CRUD de productos, categorías, usuarios) =====
    path('ecommerce/api/v1/', include(router.urls)),      
    # ===== AUTENTICACIÓN =====
    path('ecommerce/api/v1/registro/', RegistroUsuarioView.as_view(), name='registro'),
    path('ecommerce/api/v1/login/', LoginView.as_view(), name='login'),    
    path('ecommerce/api/v1/logout/', LogoutView.as_view(), name='logout'),    
    path('ecommerce/api/v1/perfil/', userProfileView.as_view(), name='perfil'),    
    # ===== DOCUMENTACIÓN (Swagger) =====
    path('ecommerce/api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('ecommerce/api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),        
]