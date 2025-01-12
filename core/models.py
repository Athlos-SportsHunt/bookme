from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_host = models.BooleanField(default=False)
    
    def __str__(self):
        if self.is_host:
            return f"{self.username} (Host)"
        return self.username
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey("host.Booking", on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    order_timestamp = models.DateTimeField(auto_now_add=True)
    signature = models.CharField(max_length=255, blank=True, null=True)
