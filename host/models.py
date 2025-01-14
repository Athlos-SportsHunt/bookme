from django.db import models
from core.models import User
from datetime import datetime
from django.core.exceptions import ValidationError

# Create your models here.
class Venue(models.Model):
    # hosts
    name = models.CharField(max_length=100)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    # address, gmaps link

    def save(self, *args, **kwargs):
        if not self.host.is_host:
            raise ValidationError("Only hosts can create venues")
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name}"

class Turf(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='turf_venue')
    name = models.CharField(max_length=100) # turf name: 5-a-side, 7-a-side, 11-a-side or football, cricket, etc.
    price_per_hr = models.DecimalField(max_digits=6, decimal_places=2) # price per hour
    # bookings
    #  opening and closing hours
    #  available days
    # special rate on holidays (opt)
    
    # add some thing like maintenance timing and stuff
    
     
    def clean(self):
        self.name = self.name.strip()
        # Check if any turfs in the venue have the same exact name
        if Turf.objects.filter(venue=self.venue, name=self.name).exclude(pk=self.pk).exists():
            raise ValidationError('A turf with this name already exists in the venue.')
        
    def save(self, *args, **kwargs):
        self.clean()  # Call the clean method to perform validation
        super().save(*args, **kwargs)  # Call the real save() method
        
    def __str__(self):
        return f"{self.venue.name} -> {self.name}"
    



class Booking(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='turf_booking')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=6, decimal_places=2)
    
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    
    class Meta:
        unique_together = ('turf', 'start_datetime', 'end_datetime')
    
    def _validate_time_slots(self):
        if self.start_datetime.minute not in [0, 30] or self.end_datetime.minute not in [0, 30]:
            raise ValidationError('Start and end times must be on the hour or half-hour.')
        # if booking conflicts with maintenance time

    def _validate_booking_order(self):
        if self.end_datetime <= self.start_datetime:
            raise ValidationError('End time must be after start time.')
        if self.start_datetime < datetime.now():
            raise ValidationError('Booking cannot be in the past.')

    def _check_overlap(self):
        overlapping_bookings = Booking.objects.filter(
            turf=self.turf,
            start_datetime__lt=self.end_datetime,
            end_datetime__gt=self.start_datetime
        ).exclude(pk=self.pk)
        
        if overlapping_bookings.exists():
            raise ValidationError('This booking overlaps with another booking.')

    def clean(self):
        self._validate_time_slots()
        self._validate_booking_order()
        self._check_overlap()
        
    
    def save(self, *args, **kwargs):
        self.clean()  # Validate before saving
        if not self.pk:  # Only calculate total_price on creation
            duration = (self.end_datetime - self.start_datetime).total_seconds() / 3600.0  # duration in hours
            self.total_price = duration * self.turf.price_per_hr
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.turf.venue.name} -> {self.turf.name} -> {self.start_datetime} to {self.end_datetime}"

