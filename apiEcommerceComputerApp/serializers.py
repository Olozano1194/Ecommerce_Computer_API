from rest_framework import serializers
from .models import Usuario, Producto, Categoria
#token
from rest_framework.authtoken.models import Token

class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ('id','fecha_creacion',)

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ('id',)

