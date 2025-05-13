from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from warehouses.models import Product
from warehouses.serializers import ProductSerializer


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


