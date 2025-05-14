from rest_framework import serializers
from .models import Store, FavoriteWarehouse
from warehouses.models import Warehouse

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

class WarehouseSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'company_name', 'address']

class FavoriteWarehouseSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSimpleSerializer()

    class Meta:
        model = FavoriteWarehouse
        fields = ['id', 'warehouse']
