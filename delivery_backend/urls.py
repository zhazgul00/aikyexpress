from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/accounts/', include('accounts.urls')),
    path('api/stores/', include('stores.urls')),
    path('api/drivers/', include('drivers.urls')),
    path('api/warehouses/', include('warehouses.urls')),
    path('api/orders/', include('orders.urls')),
]
