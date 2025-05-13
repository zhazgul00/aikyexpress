from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)


    company_name = serializers.CharField(required=False)
    address = serializers.CharField(required=False)


    vehicle_type = serializers.CharField(required=False)
    vehicle_number = serializers.CharField(required=False)
    capacity = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = (
            'username', 'password', 'password2', 'role',
            'company_name', 'address',
            'vehicle_type', 'vehicle_number', 'capacity',
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Пароли не совпадают")

        role = attrs.get('role')

        # Проверка нужных полей в зависимости от роли
        if role == 'warehouse':
            if not attrs.get('company_name'):
                raise serializers.ValidationError({"company_name": "Обязательное поле для склада"})
            if not attrs.get('address'):
                raise serializers.ValidationError({"address": "Обязательное поле для склада"})

        elif role == 'store':
            if not attrs.get('address'):
                raise serializers.ValidationError({"address": "Обязательное поле для магазина"})

        elif role == 'driver':
            for field in ['vehicle_type', 'vehicle_number', 'capacity']:
                if not attrs.get(field):
                    raise serializers.ValidationError({field: f"Обязательное поле для водителя"})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')

        # остальные поля останутся в request.data, ты используешь их в view
        user = CustomUser.objects.create(**{
            "username": validated_data["username"],
            "role": validated_data["role"]
        })
        user.set_password(password)
        user.save()
        return user
