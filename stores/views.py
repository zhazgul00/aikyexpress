from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from warehouses.models import Product

class StoreDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'store':
            return Response({'error': 'Access denied'}, status=403)

        products = Product.objects.all()
        return Response({'products': [str(p) for p in products]})
