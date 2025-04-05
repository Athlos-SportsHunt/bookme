from rest_framework import serializers
from host.models import Venue, Turf

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
