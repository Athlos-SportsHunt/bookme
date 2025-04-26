from rest_framework import serializers
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import razorpay

from host.models import Venue, Turf, Booking
from .models import Order

class TurfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turf
        fields = ['id', 'name', 'price_per_hr']

class VenueSerializer(serializers.ModelSerializer):
    turfs = TurfSerializer(many=True, read_only=True)  # This will show all turfs associated with the venue
    host_name = serializers.CharField(source='host.username', read_only=True)  # Just show host's name

    class Meta:
        model = Venue
        fields = ['id', 'name', 'host_name', 'turfs']


class CreateOrderSerializer(serializers.Serializer):
    venue_id = serializers.IntegerField()
    turf_id = serializers.IntegerField()
    start_date = serializers.DateTimeField()
    duration = serializers.IntegerField(min_value=60)

    def validate(self, data):
        # Validate that the turf belongs to the venue
        try:
            turf = Turf.objects.get(id=data['turf_id'], venue_id=data['venue_id'])
        except Turf.DoesNotExist:
            raise serializers.ValidationError({'turf_id': 'Invalid turf for this venue'})

        # Handle datetime timezone
        start_time = data['start_date']
        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time)
        start_time = timezone.localtime(start_time)

        # Validate duration and calculate end time
        duration_mins = data['duration']
        if duration_mins % 30 != 0:
            raise serializers.ValidationError({'duration': 'Duration must be in increments of 30 minutes'})

        # Validate that start time minutes are in 30-minute increments
        if start_time.minute not in (0, 30):
            raise serializers.ValidationError({'start_date': 'Start time minutes must be either 00 or 30'})

        end_time = start_time + timezone.timedelta(minutes=duration_mins)

        # Validate that booking is not in the past
        if start_time < timezone.now():
            raise serializers.ValidationError({'start_date': 'Booking cannot be in the past'})

        # Check for overlapping bookings
        overlapping = Booking.objects.filter(
            turf=turf,
            start_datetime__lt=end_time,
            end_datetime__gt=start_time,
            verified=True
        )
        if overlapping.exists():
            raise serializers.ValidationError('This time slot is already booked')

        # Calculate total price
        total_duration = Decimal(duration_mins) / Decimal(60)  # Convert to hours
        total_price = (turf.price_per_hr * total_duration * 100).to_integral()  # Convert to paise

        # Create Razorpay order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        receipt_id = f'booking_{int(timezone.now().timestamp())}'

        order_data = {
            'amount': int(total_price),
            'currency': 'INR',
            'receipt': receipt_id,
            'notes': {
                'turf_id': turf.id,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration': duration_mins
            }
        }

        razorpay_order = client.order.create(order_data)

        # Add validated data
        data['turf'] = turf
        data['start_datetime'] = start_time
        data['end_datetime'] = end_time
        data['amount'] = total_price
        data['razorpay_order'] = razorpay_order
        
        return data
