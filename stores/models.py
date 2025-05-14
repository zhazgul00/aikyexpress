from django.db import models
from accounts.models import CustomUser
from warehouses.models import Warehouse

class Store(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)


class FavoriteWarehouse(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='favorites')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('store', 'warehouse')