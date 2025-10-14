from rest_framework import permissions

class IsAdministrador(permissions.BasePermission):
    """
    Permiso que solo permite acceso a administradores
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'ADMIN'

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite edición solo al dueño del objeto
    """
    def has_object_permission(self, request, view, obj):
        # Los métodos seguros (GET, HEAD, OPTIONS) siempre permitidos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions solo para el dueño
        return obj.usuario == request.user

class ReadOnlyOrAdmin(permissions.BasePermission):
    """
    Permiso que permite lectura a todos pero escritura solo a admin
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.rol == 'ADMIN'