from django.db import models
from core.models import *
from datetime import datetime
from django.core.exceptions import ValidationError

# Create your models here.
class Venue(models.Model):
    # hosts
    name = models.CharField(max_length=100)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    # address, gmaps link
    ...


class Turf(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='turf_venue')
    name = models.CharField(max_length=100) # turf name: 5-a-side, 7-a-side, 11-a-side or football, cricket, etc.
    price_per_hr = models.DecimalField(max_digits=6, decimal_places=2) # price per hour
    # bookings



class Booking(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='turf_booking')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=6, decimal_places=2)
    
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    
    class Meta:
        unique_together = ('turf', 'start_datetime', 'end_datetime')
    
    def clean(self):
        # Ensure start and end times are on the hour or half-hour
        if self.start_datetime.minute not in [0, 30] or self.end_datetime.minute not in [0, 30]:
            raise ValidationError('Start and end times must be on the hour or half-hour.')
        
        # Ensure end time is after start time
        if self.end_datetime <= self.start_datetime:
            raise ValidationError('End time must be after start time.')
        
        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            turf=self.turf,
            start_datetime__lt=self.end_datetime,
            end_datetime__gt=self.start_datetime
        ).exclude(pk=self.pk)
        
        if overlapping_bookings.exists():
            raise ValidationError('This booking overlaps with another booking.')
    
    def save(self, *args, **kwargs):
        self.clean()  # Validate before saving
        if not self.pk:  # Only calculate total_price on creation
            duration = (self.end_datetime - self.start_datetime).total_seconds() / 3600.0  # duration in hours
            self.total_price = duration * self.turf.price_per_hr
        super().save(*args, **kwargs)

