# stores/serializers.py
from rest_framework import serializers
from .models import Store, FavoriteWarehouse
from warehouses.models import Warehouse
from accounts.serializers import UserSerializer # <--- ИМПОРТИРУЙТЕ UserSerializer

class StoreSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # <--- ИЗМЕНЕНИЕ ЗДЕСЬ

    class Meta:
        model = Store
        fields = ['id', 'user', 'address'] # Явно перечислим поля для ясности
        # Если 'user' здесь не указать, но он есть в модели,
        # и вы объявили user = UserSerializer(), он все равно будет включен.

# Остальные ваши сериализаторы (WarehouseSimpleSerializer, FavoriteWarehouseSerializer) остаются без изменений.
class WarehouseSimpleSerializer(serializers.ModelSerializer):
    # ... (без изменений)
    class Meta:
        model = Warehouse
        fields = ['id', 'company_name', 'address']

class FavoriteWarehouseSerializer(serializers.ModelSerializer):
    # ... (без изменений)
    warehouse = WarehouseSimpleSerializer()
    class Meta:
        model = FavoriteWarehouse
        fields = ['id', 'warehouse']