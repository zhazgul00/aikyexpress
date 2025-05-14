from django.urls import path
from .views import (
    StoreDashboardView,
    FavoriteWarehouseListView,
    FavoriteWarehouseAddView,
)

urlpatterns = [
    path('dashboard/', StoreDashboardView.as_view(), name='store_dashboard'),
    path('favorites/', FavoriteWarehouseListView.as_view(), name='list_favorites'),
    path('favorites/manage/', FavoriteWarehouseAddView.as_view(), name='manage_favorites'),
]
