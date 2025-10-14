from rest_framework import serializers
from .models import Usuario, Producto, Categoria
from .permissions import IsAdministrador
#token
from rest_framework.authtoken.models import Token

class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)

    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ('id','fecha_creacion','creado_por', 'creado_por_nombre',)

    def validate_precio(self, value):
        """
        Validar que el precio sea positivo.
        """
        if value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor a 0.')
        return value
    
    def create(self, validated_data):
        """
        Al crear un producto, asignar automáticamente el usuario actual como creador.
        """

        # Asignamos el usuario actual como creador
        validated_data['creado_por'] = self.context['request'].user

        # Si el usuario no es admin, forzar algunos valores
        user = self.context['request'].user
        if user.roles != 'admin':
            # usuarios normales no pueden marcar productos como nuevos o más vendidos
            validated_data['es_mas_vendido'] = False
            validated_data['es_nuevo'] = False
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Restricciones en la actualización según el rol
        """
        user = self.context['request'].user
        # si el usuario no es admin, no puede modificar ciertos campos
        if user.roles != 'admin':
            if 'es_mas_vendido' in validated_data:
                validated_data.pop('es_mas_vendido')
            if 'es_nuevo' in validated_data:
                validated_data.pop('es_nuevo')
            if 'creado_por' in validated_data:
                validated_data.pop('creado_por')

        return super().update(instance, validated_data)

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ('id',)
    
    def validate_nombre(self, value):
        """
        Validad que el nombre de la categoría sea único.
        """
        if self.instance: # si es una actualización
            if Categoria.objects.exclude(pk=self.instance.pk).filter(nombre_iexact=value).exists():
                raise serializers.ValidationError('Ya existe una categoría con este nombre.')
            else: # Si es una creación
                if Categoria.objects.filter(nombre__iaexact=value).exists():
                    raise serializers.ValidationError('Ya existe una categoría con este nombre.')
            return value

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = '__all__'
        read_only_fields = ('id','created_at', 'is_active', 'roles',)

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("La contraseña debe tener al menos 6 caracteres")
        return value

    def create(self, validated_data):
        #ciframos la contraseña antes de crear el usuario
        password = validated_data.pop('password')
        user = Usuario(**validated_data) #creamos el usuario
        #ciframos la contraseña
        user.set_password(password)
        #guardamos el usuario
        user.save()
        #Generamos el token para poder loguearse
        # token = Token.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        try:
            # avatar = validated_data.get('avatar')
            # print(f"Avatar recibido: {avatar}")
            # Manejo de la contraseña
            if 'password' in validated_data:
                password = validated_data.pop('password')
                instance.set_password(password)
            
            # Manejo del avatar
            # if 'avatar' in validated_data:
            #     instance.avatar = validated_data['avatar']

            # Actualizar los demás campos
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            instance.save()
            return instance
            
        except Exception as e:
            print("Error en el serializer update:", str(e))
            raise 