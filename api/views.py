from django.http import JsonResponse
from .utils import BookingValidation
from host.models import Booking

# Create your views here.
def handle_booking(req):
    validator = BookingValidation(req)
    validation_result = validator.validate()

    if not validation_result["is_valid"]:
        return JsonResponse({"errors": validation_result.get("errors", [validation_result.get("error")])}, status=400)

    booking = Booking(
        turf=validation_result["turf"],
        user=req.user,
        start_datetime=validation_result["start_time"],
        end_datetime=validation_result["end_time"]
    )
    booking.save()
    
    return JsonResponse({"message": "Booking successfully!", })
