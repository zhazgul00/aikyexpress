from django.urls import path
from .views import RegisterAPIView, DashboardAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    MeAPIView,
)


urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    path('me/', MeAPIView.as_view(), name='me'),
]
