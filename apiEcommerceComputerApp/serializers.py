from rest_framework import serializers
from .models import Usuario, Producto, Categoria, ImagenProducto
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class CategoriaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Categoría.
    """
    cantidad_productos = serializers.SerializerMethodField()

    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ['id']
    
    def get_cantidad_productos(self, obj):
        """
        Retorna la cantidad de productos de esta categoría.
        """
        return obj.productos.count()

    def validate_nombre(self, value):
        """
        Validad que el nombre de la categoría sea único.
        """
        qs = Categoria.objects.filter(nombre_iexact=value)
        if self.instance: # si es una actualización
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Ya existe una categoría con este nombre.')
        return value

class ImagenProductoSerializer(serializers.ModelSerializer):
    """
    Serializer para las imágenes adicionales de productos.
    """
    class Meta:
        model = ImagenProducto
        fields = '__all__'
        read_only_fields = ['id']

class ProductoListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar productos. Reutiliza los campos ya presentes en tu modelo:
    - rating  <- corresponde al float que guardas
    - cantidad_vendida <- entero que guardas
    """
    # Campos computados que añadimos desde la queryset (annotate)
    average_rating = serializers.FloatField(read_only=True)
    cantidad_vendida = serializers.IntegerField(read_only=True)
    
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    imagen_principal = serializers.SerializerMethodField()    
    # tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    # Campos calculados
    es_mas_vendido = serializers.BooleanField(read_only=True)
    esta_agotado = serializers.BooleanField(read_only=True)
    stock_bajo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ['id', 'es_nuevo', 'cantidad_vendida', 'average_rating', 'imagen_principal']
    
    def get_imagen_principal(self, obj):
        imagenes = getattr(obj, 'imagenes', None)
        if imagenes:
            return getattr(first, 'imagen', None)
        return getattr(obj, 'imagen', None)
    
class ProductoDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para ver el detalle de un producto.
    Incluye todas las imágenes adicionales.
    """
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source='categoria',
        write_only=True
    )
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    # Imágenes adicionales
    imagenes_adicionales = ImagenProductoSerializer(many=True, read_only=True)
    # Campos calculados
    es_mas_vendido = serializers.BooleanField(read_only=True)
    esta_agotado = serializers.BooleanField(read_only=True)
    stock_bajo = serializers.BooleanField(read_only=True)

    # Información del creador
    creado_por_nombre = serializers.CharField(
        source='creado_por.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ['id', 'es_nuevo', 'cantidad_vendida', 'fecha_creacion', 'fecha_actualizacion']

    def validate_precio(self, value):
        """
        Valida que el precio sea positivo.
        """
        if value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor a 0.')
        return value
    
    def validate_stock(self, value):
        """
        Valida que el stock no sea negativo.
        """
        if value < 0:
            raise serializers.ValidationError('El stock no puede ser negativo.')
        return value

    def create(self, validated_data):
        """
        Al crear un producto, asignar automáticamente el usuario actual como creador.
        """

        request = self.context['request']
        if request and hasattr(request, 'user'):
            validated_data['creado_por'] = request.user
        
        # Validación adicional para usuarios no admin
        user = request.user if request else None
        if user and user.roles != 'admin':
            # Los usuarios normales no pueden marcar productos como nuevos o más vendidos
            validated_data.pop('es_mas_vendido', None)
            validated_data.pop('es_nuevo', None)

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Restricciones en la actualización según el rol del usuario.
        """
        request = self.context.get('request')
        user = request.user if request else None

        if user and user.roles != 'admin':
            if 'es_mas_vendido' in validated_data:
                validated_data.pop('es_mas_vendido')            
            if 'creado_por' in validated_data:
                validated_data.pop('creado_por')

        return super().update(instance, validated_data)

class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """
    Serializer para el registro de nuevos usuarios.
    Automáticamente los marca como 'cliente'.
    """
    password = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
        # validators=[validate_password]
    )

    # password_confirmacion = serializers.CharField(
    #     write_only=True,
    #     required=True,
    #     # style={'input_type': 'password'}
    # )

    class Meta:
        model = Usuario
        fields = '__all__'
        read_only_fields = ['id','created_at', 'is_active']
        extra_kwargs = {
            'email': {'required': True},
            'nombre': {'required': True},
            'apellido': {'required': True}
        }

    def validate_correo(self, value):
        """
        Valida que el correo no esté registrado.
        """
        if Usuario.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Este correo ya está registrado.')
        return value.lower()

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("La contraseña debe tener al menos 6 caracteres")
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        """
        Crea el usuario y automaticamente lo asigna al rol 'cliente'.
        """
        usuario = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nombre=validated_data.get('nombre', ''),
            apellido=validated_data.get('apellido', '')
        )        
        # Asegura que sea cliente
        usuario.roles = 'cliente'
        usuario.save()        
        # Crea automáticamente el token de autenticación
        # Token.objects.create(user=usuario)
        
        return usuario

    def to_representation(self, instance):
        """
        Controla qué datos se devuelven después de crear el usuario.
        """
        data = super().to_representation(instance)
        data.pop('password', None)  # Asegurarse de que la contraseña no se devuelva
        return data

class UsuarioSerializer(serializers.ModelSerializer):
    """"
    Serializer para ver y actualizar el perfil del usuario.
    """
    nombre_completo = serializers.CharField(
        source='get_full_name',
        read_only=True
    )
    rol_display = serializers.CharField(
        source='get_roles_display',
        read_only=True
    )

    class Meta:
        model = Usuario
        fields = '__all__'
        read_only_fields = ['id','correo', 'roles', 'is_active', 'Created_at']        

    def update(self, instance, validated_data):
        """
        Actualiza solo nombre y apellido.
        El correo y rol no se pueden cambiar.
        """
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.apellido = validated_data.get('apellido', instance.apellido)
        instance.save()
        return instance

class CambiarPasswordSerializer(serializers.Serializer):
    """Serializer para cambiar la contraseña del usuario"""
    password_actual = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    password_nueva = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    password_confirmacion = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_password_actual(self, value):
        """Valida que la contraseña actual sea correcta"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('La contraseña actual es incorrecta.')
        return value
    
    def validate_password_nueva(self, value):
        """Valida la fortaleza de la nueva contraseña"""
        if len(value) < 6:
            raise serializers.ValidationError(
                'La contraseña debe tener al menos 6 caracteres.'
            )
        
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        return value
    
    def validate(self, data):
        """Valida que las contraseñas nuevas coincidan"""
        if data['password_nueva'] != data['password_confirmacion']:
            raise serializers.ValidationError({
                'password_confirmacion': 'Las contraseñas no coinciden.'
            })
        return data
    
    def save(self):
        """Cambia la contraseña del usuario"""
        user = self.context['request'].user
        user.set_password(self.validated_data['password_nueva'])
        user.save()
        return user