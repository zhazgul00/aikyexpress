from django.db import models
from accounts.models import CustomUser
from warehouses.models import Warehouse

from django.db import models
from accounts.models import CustomUser
from warehouses.models import Warehouse

class Driver(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField()

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

