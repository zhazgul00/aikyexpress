from rest_framework import serializers
from .models import CustomUser, Driver, Store, Warehouse
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'password2', 'role')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        validated_data.pop('password2')

        user = CustomUser.objects.create(role=role, **validated_data)
        user.set_password(password)
        user.save()
        return user
