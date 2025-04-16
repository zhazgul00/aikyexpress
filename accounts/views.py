from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from .models import Driver, Store, Warehouse

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
