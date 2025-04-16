from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer
from stores.models import Store
from rest_framework.permissions import IsAuthenticated

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'store':
            store = Store.objects.get(user=user)
            return Order.objects.filter(store=store)
        return Order.objects.all()

    def perform_create(self, serializer):
        store = Store.objects.get(user=self.request.user)
        serializer.save(store=store, status='new')
