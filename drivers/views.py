from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from orders.models import Order
from .models import Driver
from rest_framework.permissions import IsAuthenticated

class DriverDashboardView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        if request.user.role != 'driver':
            return Response({'error': 'Access denied'}, status=403)

        orders = Order.objects.filter(driver=None)
        return Response({'available_orders': [str(o) for o in orders]})

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
