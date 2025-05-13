from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CreateOrderView
from django.urls import path, include

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='orders')

urlpatterns = [
    path('view/', include(router.urls)),
    path('', CreateOrderView.as_view(), name='create_order'),
]
