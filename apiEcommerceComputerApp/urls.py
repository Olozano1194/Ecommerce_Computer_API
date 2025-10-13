from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import ProductoViewSet, CategoriaViewSet, ProductosNuevosViewSet, MasVendidosViewSet, ProductosPorTipoViewSet, UserViewSet

#api versioning
router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'productos-nuevos', ProductosNuevosViewSet, basename='productos-nuevo')
router.register(r'mas-vendidos', MasVendidosViewSet, basename='mas-vendido')
router.register(r'usuarios', UserViewSet, basename='usuario')


urlpatterns = [
    path('ecommerce/api/v1/', include(router.urls)),      
    
    path('ecommerce/api/v1/productos-tipo/<str:tipo>/', ProductosPorTipoViewSet.as_view({'get': 'list'}), name='productos-tipo'),
    path('ecommerce/api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('ecommerce/api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # path('gym/api/v1/home/', Home.as_view(), name='home'),
    # path('gym/api/v1/membership-notifications/', membership_notifications, name='membership-notifications'),    
]