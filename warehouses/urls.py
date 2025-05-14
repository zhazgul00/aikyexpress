from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CreateWarehouseDriverAPIView, WarehouseDriversListAPIView
from django.urls import path, include

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
    path('drivers/create/', CreateWarehouseDriverAPIView.as_view(), name='create_driver_by_warehouse'),
    path('drivers/', WarehouseDriversListAPIView.as_view(), name='list_drivers_by_warehouse'), 
]
