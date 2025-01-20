from datetime import datetime, timedelta
from host.models import *
from django.core.exceptions import ValidationError
import json

class BookingValidation:
    def __init__(self, req):
        self.req = req

    def validate(self):
        data = json.loads(self.req.body.decode('utf-8'))
        venue_id = data.get('venue_id')
        turf_id = data.get('turf_id')
        start_time_str = data.get('start_date')
        
        try:
            duration_mins = int(data.get('duration'))
            if duration_mins < 60 or duration_mins % 30 != 0:
                return {"is_valid": False, "error": "Duration must be at least 60 minutes and in increments of 30 minutes"}
        except (ValueError, TypeError):
            return {"is_valid": False, "error": "Invalid duration format"}

        validation_result = self._validate_input(venue_id, turf_id, start_time_str, duration_mins)
        if not validation_result["is_valid"]:
            return validation_result

        start_time = validation_result["start_time"]
        end_time = start_time + timedelta(minutes=duration_mins)

        validation_result = self._validate_turf(venue_id, turf_id)
        if not validation_result["is_valid"]:
            return validation_result

        turf = validation_result["turf"]

        validation_result = self._validate_availability(turf, start_time, end_time)
        if not validation_result["is_valid"]:
            return validation_result

        return {"is_valid": True, "start_time": start_time, "end_time": end_time, "turf": turf}

    def _validate_input(self, venue_id, turf_id, start_time_str, duration_mins):
        errors = []

        if not venue_id:
            errors.append("Missing venue ID")
        if not turf_id:
            errors.append("Missing turf ID")
        if not start_time_str:
            errors.append("Missing start time")
        if not duration_mins:
            errors.append("Missing duration")
        try:
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            errors.append("Invalid start time format")

        if errors:
            return {"is_valid": False, "errors": errors}

        return {"is_valid": True, "start_time": start_time}

    def _validate_turf(self, venue_id, turf_id):
        try:
            turf = Turf.objects.get(id=turf_id, venue_id=venue_id)
        except Turf.DoesNotExist:
            return {"is_valid": False, "error": "Venue, Turf does not exist"}

        return {"is_valid": True, "turf": turf}

    def _validate_availability(self, turf, start_time, end_time):
        overlapping_bookings = Booking.objects.filter(
            turf=turf,
            start_datetime__lt=end_time,
            end_datetime__gt=start_time
        )

        if overlapping_bookings.exists():
            return {"is_valid": False, "error": "The selected time slot is not available"}

        return {"is_valid": True}
    
class CreateVenueValidation:
    def __init__(self, req):
        self.req = req
        self.data = json.loads(req.body.decode('utf-8'))
        self.validated_data = {}

    def validate(self):
        validation_methods = [
            self._validate_venue_name,
            # Add more validation methods here as needed
        ]

        for method in validation_methods:
            result = method()
            if not result["is_valid"]:
                return result

        return {"is_valid": True, "validated_data": self.validated_data}

    def _validate_venue_name(self):
        venue_name = self.data.get('venue_name')
        if not venue_name:
            return {"is_valid": False, "error": "Venue name is required"}

        if Venue.objects.filter(name=venue_name).exists():
            return {"is_valid": False, "error": "Venue with this name already exists"}

        self.validated_data['venue_name'] = venue_name
        return {"is_valid": True}