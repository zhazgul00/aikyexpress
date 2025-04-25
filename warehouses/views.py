from rest_framework import viewsets, permissions
from .models import Product, Warehouse
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated

class IsWarehouse(permissions.BasePermission):
    permission_classes = [IsAuthenticated]
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'warehouse'

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsWarehouse]

    def get_queryset(self):
        user = self.request.user
        warehouse = Warehouse.objects.get(user=user)
        queryset = Product.objects.filter(warehouse=warehouse)

        name = self.request.query_params.get('name')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if name:
            queryset = queryset.filter(name__icontains=name)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset


    def perform_create(self, serializer):
        warehouse = Warehouse.objects.get(user=self.request.user)
        serializer.save(warehouse=warehouse)
