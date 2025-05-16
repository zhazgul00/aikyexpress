from rest_framework import serializers
from .models import Order
from warehouses.models import Product
from stores.serializers import StoreSerializer
from warehouses.serializers import ProductSerializer

class OrderSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    title = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()
    warehouse_name = serializers.SerializerMethodField()
    warehouse_address = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'product', 'store', 'driver', 'quantity',
            'status', 'created_at', 'updated_at',
            'title', 'address', 'items',
            'store_name', 'product_price',
            'warehouse_name', 'warehouse_address',
        ]
        read_only_fields = ('status', 'created_at', 'updated_at')

    def get_title(self, obj):
        return f"{obj.product.name} ({obj.quantity} шт)"

    def get_address(self, obj):
        return obj.store.address if obj.store and obj.store.address else "Адрес не указан"

    def get_items(self, obj):
        return obj.quantity

    def get_store_name(self, obj):
        return obj.store.user.username if obj.store and obj.store.user else "Неизвестный магазин"

    def get_product_price(self, obj):
        return obj.product.price if obj.product else None

    def get_warehouse_name(self, obj):
        if obj.product and obj.product.warehouse:
            return obj.product.warehouse.company_name
        return "Неизвестный склад"

    def get_warehouse_address(self, obj):
        if obj.product and obj.product.warehouse:
            return obj.product.warehouse.address
        return "Адрес склада неизвестен"



class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['product', 'quantity'] # 'product' здесь по умолчанию будет PrimaryKeyRelatedField

    def validate(self, data):
        product = data.get('product') # Это будет экземпляр Product
        quantity = data.get('quantity')

        if product and quantity: # Проверяем, что оба поля присутствуют
            if product.quantity < quantity:
                raise serializers.ValidationError(
                    {'error': f'Недостаточно товара "{product.name}" на складе. Доступно: {product.quantity}, Запрошено: {quantity}'}
                )
        # Если product или quantity не предоставлены, стандартные валидаторы DRF
        # (например, is_required=True по умолчанию для полей модели) должны выдать ошибку.
        # Если вы хотите более кастомные сообщения:
        # if not product:
        #     raise serializers.ValidationError({'product': 'Это поле обязательно.'})
        # if not quantity:
        #     raise serializers.ValidationError({'quantity': 'Это поле обязательно.'})
        return data