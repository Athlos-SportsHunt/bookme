from datetime import datetime, timedelta
from host.models import *
from django.core.exceptions import ValidationError
import json
from django.core.validators import URLValidator


class BookingValidation:
    def __init__(self, req):
        self.req = req
        self.data = json.loads(req.body.decode('utf-8'))
        self.validated_data = {}
        print(f"Initialization data: {self.data}")

    def validate(self):
        validation_methods = [
            self._validate_input,
            self._validate_turf,
            self._validate_availability,
        ]

        for method in validation_methods:
            result = method()
            if not result["is_valid"]:
                return result

        return {"is_valid": True, "validated_data": self.validated_data}

    def _validate_input(self):
        venue_id = self.data.get('venue_id')
        turf_id = self.data.get('turf_id')
        start_time_str = self.data.get('start_date')
        duration_mins = self.data.get('duration')
        print(f"Input data: {venue_id}, {turf_id}, {start_time_str}, {duration_mins}")
        errors = []

        if not venue_id:
            errors.append("Missing venue ID")   
        if not turf_id:
            errors.append("Missing turf ID")
        if not start_time_str:
            errors.append("Start time is required")
        else:
            try:
                start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                errors.append("Invalid start time format")
        if not duration_mins:
            errors.append("Missing duration")
        try:
            duration_mins = int(duration_mins)
            if duration_mins < 60 or duration_mins % 30 != 0:
                errors.append("Duration must be at least 60 minutes and in increments of 30 minutes")
        except (ValueError, TypeError):
            errors.append("Invalid duration format")
        try:
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            errors.append("Invalid start time format")

        if errors:
            return {"is_valid": False, "errors": errors}

        self.validated_data['venue_id'] = venue_id
        self.validated_data['turf_id'] = turf_id
        self.validated_data['start_time'] = start_time
        self.validated_data['duration_mins'] = duration_mins
        self.validated_data['end_time'] = start_time + timedelta(minutes=duration_mins)

        return {"is_valid": True,"validated_data": self.validated_data}

    def _validate_turf(self):
        venue_id = self.validated_data['venue_id']
        turf_id = self.validated_data['turf_id']

        try:
            turf = Turf.objects.get(id=turf_id, venue_id=venue_id)
        except Turf.DoesNotExist:
            return {"is_valid": False, "error": "Venue, Turf does not exist"}

        self.validated_data['turf'] = turf
        return {"is_valid": True}

    def _validate_availability(self):
        turf = self.validated_data['turf']
        start_time = self.validated_data['start_time']
        end_time = self.validated_data['end_time']

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
        self.files = req.FILES  # Uploaded files
        self.validated_data = {}

    def validate(self):
        validation_methods = [
            self._validate_venue_name,
            self._validate_image,
            self._validate_google_maps_link
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
    
    def _validate_image(self):
        image = self.files.get('image')
        if not image:
            return {"is_valid": False, "error": "Turf image is required"}

        # Validate file type
        allowed_types = ["image/jpeg", "image/png"]
        if image.content_type not in allowed_types:
            return {"is_valid": False, "error": "Invalid image format. Allowed: JPEG, PNG"}

        self.validated_data['image'] = image
        return {"is_valid": True}
    
    def _validate_google_maps_link(self):
        gmaps_link = self.data.get('google_maps_link', '').strip()
        if not gmaps_link:
            return {"is_valid": True}  # It's optional, so return valid if empty

        url_validator = URLValidator()
        try:
            url_validator(gmaps_link)
        except ValidationError:
            return {"is_valid": False, "error": "Invalid Google Maps link"}

        self.validated_data['google_maps_link'] = gmaps_link
        return {"is_valid": True}
    
    def _validate_address(self):
        address = self.data.get('address', '').strip()
        if not address:
            return {"is_valid": False, "error": "Address is required"}

        self.validated_data['address'] = address
        return {"is_valid": True}
    
    
class CreateTurfValidation:
    def __init__(self, req, venue_id):
        self.req = req
        self.venue_id = venue_id
        self.data = json.loads(req.body.decode('utf-8'))
        self.files = req.FILES  # Uploaded files
        self.validated_data = {}

    def validate(self):
        validation_methods = [
            # self._validate_venue_id,
            
            self._validate_turf_name,
            self._validate_price_per_hr,
            self._validate_turf_image,
            self._validate_sport_id,
            self._validate_amenities
            # Add more validation methods here as needed
        ]

        for method in validation_methods:
            result = method()
            if not result["is_valid"]:
                return result

        return {"is_valid": True, "validated_data": self.validated_data}


    def _validate_turf_name(self):
        turf_name = self.data.get('turf_name')
        if not turf_name:
            return {"is_valid": False, "error": "Turf name is required"}

        if Turf.objects.filter(name=turf_name, venue=self.venue_id).exists():
            return {"is_valid": False, "error": "Turf with this name already exists in the venue"}

        self.validated_data['turf_name'] = turf_name
        return {"is_valid": True}

    def _validate_price_per_hr(self):
        price_per_hr = self.data.get('price_per_hr')
        try:
            price_per_hr = Decimal(price_per_hr)
            if price_per_hr <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return {"is_valid": False, "error": "Invalid price per hour"}

        self.validated_data['price_per_hr'] = price_per_hr
        return {"is_valid": True}
    
    def _validate_turf_image(self):
        image = self.files.get('image')  # Getting the uploaded image

        if not image:
            return {"is_valid": False, "error": "Turf image is required"}

        # Validate file type
        allowed_types = ["image/jpeg", "image/png"]
        if image.content_type not in allowed_types:
            return {"is_valid": False, "error": "Invalid image format. Allowed: JPEG, PNG"}

        self.validated_data['image'] = image
        return {"is_valid": True}
    
    def _validate_sport_id(self):
        sport_id = self.data.get('sport_id')
        if not sport_id:
            return {"is_valid": False, "error": "Sport ID is required"}

        try:
            sport = Sport.objects.get(id=sport_id)
            self.validated_data['sport'] = sport  # Save the actual sport instance
        except Sport.DoesNotExist:
            return {"is_valid": False, "error": "Invalid sport ID"}
        return {"is_valid": True}

    def _validate_amenities(self):
        amenities = self.data.get('amenities', [])
        if not isinstance(amenities, list):
            return {"is_valid": False, "error": "Amenities must be a list"}

        self.validated_data['amenities'] = amenities
        return {"is_valid": True}