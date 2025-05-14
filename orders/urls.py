from django.urls import path, include
from .views import OrderViewSet, CreateOrderView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='orders')

urlpatterns = [
    path('create/', CreateOrderView.as_view(), name='create_order'), 
    path('', include(router.urls)),  
]
