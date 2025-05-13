from rest_framework import serializers
from .models import Warehouse, Product, ProductImage


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True) 
    
    class Meta:
        model = ProductImage
        fields = ['image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True) 

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['warehouse']


