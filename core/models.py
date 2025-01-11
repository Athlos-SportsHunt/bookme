from django.db import models
from django.contrib.auth.models import AbstractUser
from host.models import *

# Create your models here.
class User(AbstractUser):
    is_host = models.BooleanField(default=False)
    
    def __str__(self):
        if self.is_host:
            return f"{self.username} (Host)"
        return self.username
    
class Order(models.model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # add turf details, later