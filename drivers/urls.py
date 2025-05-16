from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DriverDashboardView, AssignOrderView, MyOrdersView, MarkOrderDeliveredView

urlpatterns = [
    path('dashboard/', DriverDashboardView.as_view(), name='driver_dashboard'),
    path('orders/<int:pk>/assign/', AssignOrderView.as_view(), name='assign_order'),
    path('orders/my/', MyOrdersView.as_view(), name='my_orders'),
    path('orders/<int:pk>/deliver/', MarkOrderDeliveredView.as_view(), name='mark_order_delivered'),

]
