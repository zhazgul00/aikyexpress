from rest_framework import viewsets, permissions
from .models import Product, Warehouse
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import CustomUser
from drivers.models import Driver

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


class CreateWarehouseDriverAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role != "warehouse":
            return Response({"error": "Only warehouses can create drivers"}, status=403)

        data = request.data
        required_fields = ["username", "password", "vehicle_type", "vehicle_number", "capacity"]

        for field in required_fields:
            if field not in data:
                return Response({"error": f"Missing field: {field}"}, status=400)

        # 1. Создаём пользователя с ролью driver
        new_user = CustomUser.objects.create_user(
            username=data["username"],
            password=data["password"],
            role="driver"
        )

        # 2. Привязываем водителя к складу
        warehouse = Warehouse.objects.get(user=user)

        Driver.objects.create(
            user=new_user,
            vehicle_type=data["vehicle_type"],
            vehicle_number=data["vehicle_number"],
            capacity=data["capacity"],
            warehouse=warehouse
        )

        return Response({"message": "Driver created and linked to warehouse "}, status=201)
