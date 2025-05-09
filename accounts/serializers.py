from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'password2', 'role')  # warehouse_id не указываем!

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Пароли не совпадают")

        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and user.is_authenticated and user.role == 'warehouse':
            if not attrs.get('warehouse_id'):
                raise serializers.ValidationError({
                    "warehouse_id": "Это поле обязательно при регистрации от склада."
                })

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')
        role = validated_data.get('role')

        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user




