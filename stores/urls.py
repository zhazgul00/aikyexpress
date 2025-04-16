from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import StoreDashboardView

urlpatterns = [
    path('dashboard/', StoreDashboardView.as_view(), name='store_dashboard'),
]
