from django.shortcuts import render
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .models import *
from django.contrib.auth import logout
from django.urls import reverse
from django.conf import settings
from host.models import *
import razorpay
from django.views.decorators.csrf import csrf_exempt


def index(req):

    venues = Venue.objects.all()
    return render(req, "core/pages/index.html", {"venues": venues})


def login_view(req):
    return HttpResponseRedirect(reverse("social:begin", args=["auth0"]))


def logout_view(req):
    logout(req)

    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
    return_to = req.build_absolute_uri(reverse("index"))
    return HttpResponseRedirect(
        f"https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}"
    )


def venue_filter_view(req):
    venue_name = req.GET.get("venue", "")
    venues = Venue.objects.filter(name__icontains=venue_name)
    if not venues:
        return render(req, "core/pages/venue_filter.html", {"error": "No venues found"})
    return render(req, "core/pages/venue_filter.html", {"venues": venues})


def venue_view(req, venue_id):
    try:
        venue = Venue.objects.get(id=venue_id)
    except Venue.DoesNotExist:
        return render(req, "core/pages/venue.html", {"error": "Venue not found"})
    return render(req, "core/pages/venue.html", {"venue": venue})


def turf_view(req, venue_id, turf_id):
    try:
        turf = Turf.objects.get(id=turf_id, venue=venue_id)
    except Turf.DoesNotExist:
        return render(req, "core/pages/turf.html", {"error": "Turf not found"})
    return render(req, "core/pages/turf.html", {"turf": turf})


def profile_view(req):
    if not req.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    bookings = Booking.objects.filter(user=req.user)
    return render(req, "core/pages/profile.html", {"bookings": bookings})


@csrf_exempt
def slot_callback(req):
    if req.method != "POST":
        return HttpResponse("Method Not Allowed", status=405)

    payment_id = req.POST.get("razorpay_payment_id", "")
    razorpay_order_id = req.POST.get("razorpay_order_id", "")
    signature = req.POST.get("razorpay_signature", "")

    if not Order.objects.filter(order_id=razorpay_order_id).exists():
        return render(req, "core/pages/slot_callback.html", {"error": "Invalid Order"})

    order = Order.objects.get(order_id=razorpay_order_id)
    order.signature = signature
    order.payment_id = payment_id
    order.save()

    razorpay_client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY)
    )
    result = razorpay_client.utility.verify_payment_signature(
        {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        }
    )

    if result is None:
        return render(
            req, "core/pages/slot_callback.html", {"error": "Invalid Signature"}
        )

    # amount = order.amount
    # razorpay_client.payment.capture(payment_id, amount)

    order.paid = True
    order.save()

    order_instance = OrderDetails.objects.get(order=order)

    order.booking = Booking.objects.create(
        turf=order_instance.turf,
        user=order_instance.user,
        start_datetime=order_instance.start_time,
        end_datetime=order_instance.end_time,
        order=order,
    )
    order.save()

    return render(
        req,
        "core/pages/slot_callback.html",
        {"message": "Slot order created successfully!"},
    )
