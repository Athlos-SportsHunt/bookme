from rest_framework import serializers
from django.utils import timezone
from .models import Venue, Turf, Sport, Booking
from core.models import User
from datetime import datetime, timedelta

class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ['id', 'name', 'description']

class CreateTurfSerializer(serializers.ModelSerializer):
    sports = serializers.PrimaryKeyRelatedField(many=True, queryset=Sport.objects.all())

    class Meta:
        model = Turf
        fields = ['name', 'sports', 'price_per_hr']
        
    def validate_name(self, value):
        value = value.strip()
        venue = self.context.get('venue')
        if venue and Turf.objects.filter(venue=venue, name=value).exists():
            raise serializers.ValidationError("A turf with this name already exists in this venue")
        return value

    def validate_sports(self, value):
        if not value:
            raise serializers.ValidationError("At least one sport is required")
        return value

    def validate_price_per_hr(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price per hour must be greater than 0")
        return value

class TurfSerializer(serializers.ModelSerializer):
    """Serializer for reading turf data"""
    sports = SportSerializer(many=True, read_only=True)

    class Meta:
        model = Turf
        fields = ['id', 'name', 'sports', 'price_per_hr']

class VenueSerializer(serializers.ModelSerializer):
    """Serializer for reading venue data"""
    turfs = TurfSerializer(many=True, read_only=True)
    
    class Meta:
        model = Venue
        fields = ['id', 'name', 'host', 'turfs']
        read_only_fields = ['host']

class CreateVenueSerializer(serializers.ModelSerializer):
    """Serializer for creating venues"""
    turfs = CreateTurfSerializer(many=True, required=False, write_only=True)

    class Meta:
        model = Venue
        fields = ['name', 'turfs']

    def validate_name(self, value):
        value = value.strip()
        if Venue.objects.filter(name=value).exists():
            raise serializers.ValidationError("A venue with this name already exists")
        return value

    def validate(self, data):
        # Validate that the user is a host
        user = self.context.get('request').user
        if not user.is_host:
            raise serializers.ValidationError("Only hosts can create venues")
        return data

    def create(self, validated_data):
        turfs_data = validated_data.pop('turfs', [])
        venue = Venue.objects.create(**validated_data)
        
        for turf_data in turfs_data:
            sports = turf_data.pop('sports')
            turf = Turf.objects.create(venue=venue, **turf_data)
            turf.sports.set(sports)
            
        return venue
        
    def to_representation(self, instance):
        # Use VenueSerializer for the response
        return VenueSerializer(instance).data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class BookingDetailsSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    turf = TurfSerializer(read_only=True)
    venue_name = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['id', 'user_details', 'turf', 'venue_name', 'start_time', 'end_time', 
                 'total_price', 'start_datetime', 'end_datetime', 'is_offline']
    
    def get_venue_name(self, obj):
        return obj.turf.venue.name

    def get_start_time(self, obj):
        return obj.get_start_time()
    
    def get_end_time(self, obj):
        return obj.get_end_time()
    
    def to_representation(self, instance):
        # Get the original representation
        data = super().to_representation(instance)
        
        # Create the new nested structure
        return {
            'id ': instance.id,
            'user': {
                'id': instance.user.id,
            },
            **data
        }

class OfflineBookingSerializer(serializers.ModelSerializer):
    venue_id = serializers.IntegerField(write_only=True)
    turf_id = serializers.IntegerField(write_only=True)
    start_date = serializers.DateTimeField(write_only=True)
    duration = serializers.IntegerField(write_only=True, min_value=60)
    
    class Meta:
        model = Booking
        fields = ['venue_id', 'turf_id', 'start_date', 'duration']

    def validate(self, data):
        # Validate that the turf belongs to the venue
        try:
            turf = Turf.objects.get(id=data['turf_id'], venue_id=data['venue_id'])
        except Turf.DoesNotExist:
            raise serializers.ValidationError({'turf_id': 'Invalid turf for this venue'})

        # Validate that the user is the host of the venue
        user = self.context['request'].user
        if not user.is_host or turf.venue.host != user:
            raise serializers.ValidationError('You must be the host of this venue')

        # Convert duration to timedelta and calculate end time
        duration_mins = data['duration']
        if duration_mins % 30 != 0:
            raise serializers.ValidationError({'duration': 'Duration must be in increments of 30 minutes'})

        # Validate that start time minutes are in 30-minute increments
        if data['start_date'].minute not in (0, 30):
            raise serializers.ValidationError({'start_date': 'Start time minutes must be either 00 or 30'})

        # Handle datetime timezone
        start_time = data['start_date']
        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time)
        start_time = timezone.localtime(start_time)
        end_time = start_time + timedelta(minutes=duration_mins)

        # Validate that booking is not in the past
        if start_time < timezone.now():
            raise serializers.ValidationError({'start_date': 'Booking cannot be in the past'})

        # Check for overlapping bookings
        overlapping = Booking.objects.filter(
            turf=turf,
            start_datetime__lt=end_time,
            end_datetime__gt=start_time
        )
        if overlapping.exists():
            raise serializers.ValidationError('This time slot overlaps with an existing booking')

        # Add validated data
        data['turf'] = turf
        data['start_datetime'] = start_time
        data['end_datetime'] = end_time
        data['is_offline'] = True
        data['verified'] = True
        
        return data

    def create(self, validated_data):
        # Remove extra fields that aren't part of the Booking model
        validated_data.pop('venue_id', None)
        validated_data.pop('duration', None)
        validated_data.pop('start_date', None)
        
        # Create the booking
        booking = Booking.objects.create(
            user=self.context['request'].user,
            **validated_data
        )
        return booking
