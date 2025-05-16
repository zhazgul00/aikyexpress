from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from orders.models import Order
from .models import Driver
from rest_framework.permissions import IsAuthenticated
from orders.serializers import OrderSerializer


class DriverDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'driver':
            return Response({'error': 'Access denied'}, status=403)

        try:
            driver = Driver.objects.get(user=user)

            if driver.warehouse:
                orders = Order.objects.filter(
                    driver=None,
                    product__warehouse=driver.warehouse
                )
            else:
                orders = Order.objects.filter(driver=None)

            # Возвращаем список напрямую
            return Response(OrderSerializer(orders, many=True).data)

        except Driver.DoesNotExist:
            return Response({'error': 'Driver profile not found'}, status=404)


class AssignOrderView(APIView):
    def post(self, request, pk):
        if request.user.role != 'driver':
            return Response({'error': 'Access denied'}, status=403)

        try:
            order = Order.objects.get(pk=pk)
            if order.driver:
                return Response({'error': 'Order already assigned'}, status=400)

            driver = Driver.objects.get(user=request.user)
            order.driver = driver
            order.status = 'assigned'
            order.save()
            return Response({'message': 'Order successfully assigned'})

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)
        
class MyOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'driver':
            return Response({'error': 'Access denied'}, status=403)

        driver = Driver.objects.get(user=request.user)
        orders = Order.objects.filter(driver=driver)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class MarkOrderDeliveredView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        if user.role != 'driver':
            return Response({'error': 'Access denied'}, status=403)

        try:
            driver = Driver.objects.get(user=user)
            order = Order.objects.get(pk=pk, driver=driver)

            if order.status == 'delivered':
                return Response({'error': 'Заказ уже завершён'}, status=400)

            order.status = 'delivered'
            order.save()

            return Response({'message': 'Заказ отмечен как доставленный'})

        except Driver.DoesNotExist:
            return Response({'error': 'Профиль водителя не найден'}, status=404)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=404)

