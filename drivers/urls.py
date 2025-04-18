from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DriverDashboardView, AssignOrderView

urlpatterns = [
    path('dashboard/', DriverDashboardView.as_view(), name='driver_dashboard'),
    path('orders/<int:pk>/assign/', AssignOrderView.as_view(), name='assign_order'),
]
