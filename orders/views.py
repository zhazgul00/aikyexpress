from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response  

from .models import Order
from .serializers import OrderSerializer
from stores.models import Store
from drivers.models import Driver



class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get('status')

        if user.role == 'store':
            store = Store.objects.get(user=user)
            qs = Order.objects.filter(store=store)
        elif user.role == 'driver':
            driver = Driver.objects.get(user=user)
            qs = Order.objects.filter(driver=driver)
        else:
            qs = Order.objects.all()

        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs


    def perform_create(self, serializer):
        store = Store.objects.get(user=self.request.user)
        serializer.save(store=store, status='new')



    @action(detail=True, methods=['patch'])
    def deliver(self, request, pk=None):
        user = request.user
        if user.role != 'driver':
            return Response({"error": "Access denied"}, status=403)

        try:
            order = self.get_object()
            driver = Driver.objects.get(user=user)

            if order.driver != driver:
                return Response({"error": "This is not your order"}, status=403)

            order.status = 'delivered'
            order.save()
            return Response({"message": "Order marked as delivered"})
        except:
            return Response({"error": "Error updating order"}, status=400)




