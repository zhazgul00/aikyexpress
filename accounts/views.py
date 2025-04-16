from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from warehouses.serializers import ProductSerializer
from orders.serializers import OrderSerializer 
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from stores.models import Store
from drivers.models import Driver
from warehouses.models import Warehouse, Product
from orders.models import Order

class RegisterAPIView(APIView):
    def post(self, request):
        role = request.data.get('role')
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Дополнительные поля по роли
            if role == 'driver':
                Driver.objects.create(
                    user=user,
                    vehicle_type=request.data.get('vehicle_type'),
                    vehicle_number=request.data.get('vehicle_number'),
                    capacity=request.data.get('capacity')
                )
            elif role == 'store':
                Store.objects.create(
                    user=user,
                    address=request.data.get('address')
                )
            elif role == 'warehouse':
                Warehouse.objects.create(
                    user=user,
                    company_name=request.data.get('company_name'),
                    address=request.data.get('address')
                )

            return Response({"message": "Пользователь зарегистрирован"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = user.role

        if role == 'warehouse':
            try:
                warehouse = Warehouse.objects.get(user=user)
            except Warehouse.DoesNotExist:
                return Response({"error": "Склад не найден"}, status=404)

            products = Product.objects.filter(warehouse=warehouse)
            return Response({
                "role": role,
                "products": ProductSerializer(products, many=True).data,
            })

        elif role == 'store':
            products = Product.objects.all()
            return Response({
                "role": role,
                "products": ProductSerializer(products, many=True).data,
            })

        elif role == 'driver':
            orders = Order.objects.filter(driver=None)
            return Response({
                "role": role,
                "available_orders": OrderSerializer(orders, many=True).data,
            })

        return Response({"error": "Неизвестная роль"}, status=400)
