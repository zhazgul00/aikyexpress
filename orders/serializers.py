from rest_framework import serializers
from .models import Order
from warehouses.models import Product # Убедитесь, что путь к Product верный

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('store', 'status', 'created_at', 'updated_at')
        depth = 1

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