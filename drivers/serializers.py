from rest_framework import serializers
from .models import Driver

class DriverSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Driver
        fields = ['id', 'username', 'vehicle_type', 'vehicle_number', 'capacity']
