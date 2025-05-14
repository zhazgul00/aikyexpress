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
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            role = request.data.get('role')

            # Изначально warehouse None
            warehouse = None

            # 🔐 Безопасная проверка авторизованного склада
            if request.user.is_authenticated and request.user.role == 'warehouse':
                try:
                    warehouse = Warehouse.objects.get(user=request.user)
                except Warehouse.DoesNotExist:
                    return Response({'error': 'Склад не найден'}, status=status.HTTP_400_BAD_REQUEST)

            if role == 'driver':
                Driver.objects.create(
                    user=user,
                    vehicle_type=request.data.get('vehicle_type'),
                    vehicle_number=request.data.get('vehicle_number'),
                    capacity=request.data.get('capacity'),
                    warehouse=warehouse  # ✅ добавляется, если есть
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

            return Response({"message": "Пользователь зарегистрирован"}, status=201)
        
        else:
            print(serializer.errors)

        return Response(serializer.errors, status=400)


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

class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }

        if user.role == "driver":
            driver = Driver.objects.get(user=user)
            data.update({
                "vehicle_type": driver.vehicle_type,
                "vehicle_number": driver.vehicle_number,
                "capacity": driver.capacity,
                "warehouse": driver.warehouse.company_name if driver.warehouse else None,
            })
        elif user.role == "store":
            store = Store.objects.get(user=user)
            data.update({
                "address": store.address,
            })
        elif user.role == "warehouse":
            warehouse = Warehouse.objects.get(user=user)
            data.update({
                "company_name": warehouse.company_name,
                "address": warehouse.address,
            })

        return Response(data)

    def patch(self, request):
        user = request.user
        data = request.data

        # Общие поля
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.set_password(data['password'])  
        user.save()

        # Роль-специфичные
        if user.role == "driver":
            driver = Driver.objects.get(user=user)
            driver.vehicle_type = data.get('vehicle_type', driver.vehicle_type)
            driver.vehicle_number = data.get('vehicle_number', driver.vehicle_number)
            driver.capacity = data.get('capacity', driver.capacity)
            driver.save()

        elif user.role == "store":
            store = Store.objects.get(user=user)
            store.address = data.get('address', store.address)
            store.save()

        elif user.role == "warehouse":
            warehouse = Warehouse.objects.get(user=user)
            warehouse.company_name = data.get('company_name', warehouse.company_name)
            warehouse.address = data.get('address', warehouse.address)
            warehouse.save()

        return Response({"message": "Профиль успешно обновлен✅"})

