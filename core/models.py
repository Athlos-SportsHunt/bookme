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
    booking = models.ForeignKey("host.Booking", on_delete=models.CASCADE, null=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    order_id = models.CharField(max_length=100, null=True, blank=True)
    signature = models.CharField(max_length=255, blank=True, null=True)
    order_timestamp = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField(default=0)
    paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.order_details.turf.venue.name} - {self.order_details.turf.name} - {self.order_details.start_time} to {self.order_details.end_time}"

class OrderDetails(models.Model):
    turf = models.ForeignKey("host.Turf", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="order_details")