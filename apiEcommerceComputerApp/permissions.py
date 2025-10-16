from rest_framework import permissions

class IsAdministrador(permissions.BasePermission):
    """
    Permiso personalizado:
    - Lectura: Permitido para todos
    - Escritura (POST, PUT, PATCH, DELETE): Solo administradores
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verifica si el usuario está autenticado y es admin
        return request.user and request.user.is_authenticated and request.user.roles == 'admin'

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado:
    - El usuario puede editar solo su propio perfil
    - Los administradores pueden editar cualquier perfil
    """
    def has_object_permission(self, request, view, obj):
        # Los métodos seguros (GET, HEAD, OPTIONS) siempre permitidos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura: solo el dueño o un admin
        return obj == request.user or request.user.roles == 'admin'

class ReadOnlyOrAdmin(permissions.BasePermission):
    """
    Permiso que permite lectura a todos pero escritura solo a admin
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.rol == 'ADMIN'