from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from warehouses.models import Product
from warehouses.serializers import ProductSerializer
from rest_framework import generics, status
from .models import FavoriteWarehouse, Store
from warehouses.models import Warehouse
from .serializers import FavoriteWarehouseSerializer



class StoreDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'store':
            return Response({'error': 'Access denied'}, status=403)

        products = Product.objects.all()


        search = request.query_params.get('q')
        if search:
            products = products.filter(name__icontains=search)

        serializer = ProductSerializer(products, many=True)
        return Response({'products': serializer.data})
    
class FavoriteWarehouseListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteWarehouseSerializer

    def get_queryset(self):
        store = Store.objects.get(user=self.request.user)
        return FavoriteWarehouse.objects.filter(store=store)

class FavoriteWarehouseAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        store = Store.objects.get(user=request.user)
        warehouse_id = request.data.get('warehouse_id')
        if not warehouse_id:
            return Response({'error': 'warehouse_id is required'}, status=400)

        warehouse = Warehouse.objects.get(id=warehouse_id)
        fav, created = FavoriteWarehouse.objects.get_or_create(store=store, warehouse=warehouse)
        if created:
            return Response({'message': 'Добавлен в избранное'})
        return Response({'message': 'Уже в избранном'})

    def delete(self, request):
        store = Store.objects.get(user=request.user)
        warehouse_id = request.data.get('warehouse_id')
        FavoriteWarehouse.objects.filter(store=store, warehouse_id=warehouse_id).delete()
        return Response({'message': 'Удалён из избранного'})
