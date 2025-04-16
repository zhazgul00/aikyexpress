from rest_framework import viewsets, permissions
from .models import Product, Warehouse
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated

class IsWarehouse(permissions.BasePermission):
    permission_classes = [IsAuthenticated]
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'warehouse'

class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    permission_classes = [IsWarehouse]

    def get_queryset(self):
        warehouse = Warehouse.objects.get(user=self.request.user)
        return Product.objects.filter(warehouse=warehouse)

    def perform_create(self, serializer):
        warehouse = Warehouse.objects.get(user=self.request.user)
        serializer.save(warehouse=warehouse)
