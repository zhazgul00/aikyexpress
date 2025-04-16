from django.db import models
from accounts.models import CustomUser

class Store(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
