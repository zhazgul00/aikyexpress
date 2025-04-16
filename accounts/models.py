from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('warehouse', 'Warehouse'),
        ('store', 'Store'),
        ('driver', 'Driver'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

class Driver(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=50)
    vehicle_number = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField()

class Store(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)

class Warehouse(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
