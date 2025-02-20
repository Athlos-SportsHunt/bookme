from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from .validation import *
from host.models import *
from core.models import *
from .decorators import *
from django.utils import timezone
import json
import razorpay
from decimal import Decimal
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY)
)


@login_required
@post_required
def create_slot_order(req):
    validator = BookingValidation(req)
    validation_result = validator.validate()

    if not validation_result["is_valid"]:
        return JsonResponse(
            {
                "errors": validation_result.get(
                    "errors", [validation_result.get("error")]
                )
            },
            status=400,
        )
    cleaned_data = validation_result["validated_data"]
    turf_instance = cleaned_data["turf"]
    start_time = cleaned_data["start_time"]
    end_time = cleaned_data["end_time"]

    total_duration = (end_time - start_time).total_seconds() / 3600

    total_price = (
        float(turf_instance.price_per_hr * Decimal(total_duration)) * 100
    )  # convert to paise

    razorpay_data = {
        "amount": total_price,
        "currency": "INR",
        "receipt": f"booking_{int(timezone.now().timestamp())}",
        "notes": {
            "booking_id": turf_instance.id,
            "start_time": f"{start_time}",
            "end_time": f"{end_time}",
            "duration": total_duration,
        },
    }
    callback_url = req.build_absolute_uri(reverse("core:slot_callback"))
    razorpay_data["amount"] = total_price
    razorpay_order = razorpay_client.order.create(razorpay_data)

    order_instance = Order.objects.create(
        user=req.user,
        order_id=razorpay_order["id"],
        amount=total_price,        
    )
    
    OrderDetails.objects.create(
        turf=turf_instance,
        user=req.user,
        start_time=start_time,
        end_time=end_time,
        order=order_instance,
    )
    

    return JsonResponse(
        {
            "message": "Slot order created successfully!",
            "order_details": razorpay_order,
            "RAZORPAY_KEY_ID": settings.RAZORPAY_KEY_ID,
            "callback_url": callback_url,
        },
        status=201,
    )


@host_required
def create_venue(req):
    validator = CreateVenueValidation(req)
    validation_result = validator.validate()

    if not validation_result["is_valid"]:
        return JsonResponse(
            {
                "errors": validation_result.get(
                    "errors", [validation_result.get("error")]
                )
            },
            status=400,
        )

    cleaned_data = validation_result["validated_data"]
    venue_name = cleaned_data["venue_name"]
    img = cleaned_data.get('img')
    description = cleaned_data.get('description', '')
    gmaps_maps_link = cleaned_data.get('gmaps_url', '')
    address = cleaned_data['address']
    
    venue = Venue.objects.create(
        name=venue_name,
        host=req.user,
        images=img,
        description=description,
        gmaps_maps_link=gmaps_maps_link,
        address=address,
    )

    return JsonResponse(
        {
            "message": "Venue created successfully!",
            "venue_id": venue.id,
            "venue_name": venue.name,
            "address": venue.address, 
        },
        status=201,
    )

@host_required
def delete_venue(req, venue_id):
    try:
        venue = Venue.objects.get(id=venue_id)
        if venue.host != req.user:
            return JsonResponse({"error": "Not authorized"}, status=403)
        venue.delete()
        return JsonResponse({"message": "Venue deleted successfully!"}, status=200)
    except Venue.DoesNotExist:
        return JsonResponse({"error": "Venue not found"}, status=404)

@host_required
def create_turf(req,venue_id):
    validator = CreateTurfValidation(req,venue_id)
    validation_result = validator.validate()

    if not validation_result["is_valid"]:   
        return JsonResponse(
            {
                "errors": validation_result.get(
                    "errors", [validation_result.get("error")]
                )
            },
            status=400,
        )

    cleaned_data = validation_result["validated_data"]
    
    # venue_id = cleaned_data["venue"]
    try:
        venue = Venue.objects.get(id=venue_id)
    except Venue.DoesNotExist:
        return JsonResponse({"error": "Venue not found"}, status=404)
        
    turf_name = cleaned_data["turf_name"]
    price_per_hr = cleaned_data["price_per_hr"]
    sport = cleaned_data['sport']
    img = cleaned_data.get('img')
    description = cleaned_data.get('description', '')
    amenities = cleaned_data.get("amenities", sport.amenities)

    turf = Turf.objects.create(
        name=turf_name,
        venue=venue,
        price_per_hr=price_per_hr,
        sport=sport,
        images=img,
        description=description,
        amenities=amenities,
    )

    return JsonResponse(
        {
            "message": "Turf created successfully!",
            "turf_id": turf.id,
            "turf_name": turf.name,
            "price_per_hr": str(turf.price_per_hr),
            "sport": sport.sport_type,
        },
        status=201,
    )


@host_required
def delete_turf(req, turf_id):
    try:
        turf = Turf.objects.get(id=turf_id)
        if turf.venue.host != req.user:
            return JsonResponse({"error": "Not authorized"}, status=403)
        turf.delete()
        return JsonResponse({"message": "Turf deleted successfully!"}, status=200)
    except Turf.DoesNotExist:
        return JsonResponse({"error": "Turf not found"}, status=404)

@host_required
def offline_slot_booking(req):
    try:
        data = json.loads(req.body.decode('utf-8'))
        print(f"Received data: {data}")
    except json.JSONDecodeError as e:
        return JsonResponse({"errors": ["Invalid JSON data"]}, status=400)
    
    validator = BookingValidation(req)
    validation_result = validator.validate()
    print(f"Validation result: {validation_result}")
    if not validation_result["is_valid"]:
        return JsonResponse(
            {
                "errors": validation_result.get(
                    "errors", [validation_result.get("error")]
                )
            },
            status=400,
        )

    cleaned_data = validation_result["validated_data"]
    turf_instance = cleaned_data["turf"]

    start_time = cleaned_data["start_time"]
    end_time = cleaned_data["end_time"]
    
    print(f"cleaned data: {cleaned_data}")
    
    booking = Booking.objects.create(
        turf=turf_instance,
        user=req.user,
        start_datetime=start_time,
        end_datetime=end_time,
        # if offline booking, add another field and set it to True
    )

    return JsonResponse(
        {
            "message": "Offline slot booking created successfully!",
            "booking_id": booking.id,
            "start_time": start_time,
            "end_time": end_time,
        },
        status=201,
    )
    
    
