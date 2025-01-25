from django.shortcuts import render, get_object_or_404
from .decorators import * 
from .models import *
# Create your views here

@host_required
def dashboard(req):
    host = req.user
    venues = host.venues.filter(host_id=host.id)
    context = {
        'venues': venues,
    }
    return render(req, 'host/pages/dashboard.html', context)

@host_required
def venue(req, venue_id):
    # Fetch the venue and any necessary context data
    venue = get_object_or_404(Venue, id=venue_id)
    turfs = Turf.objects.filter(venue=venue)
    return render(req, 'host/pages/venue.html', {'venue': venue, 'turfs': turfs})


@host_required 
def create_venue(req):
    return render(req, 'host/pages/create_venues.html')

@host_required
def create_turf(req, venue_id):  # Accept venue_id
    return render(req, 'host/pages/create_turf.html', {'venue_id': venue_id})

@host_required
def turf(req, venue_id, turf_id):
    venue = get_object_or_404(Venue, id=venue_id)
    turf = get_object_or_404(Turf, id=turf_id)
    bookings = turf.turf_booking.all()
    return render(req, 'host/pages/turf.html', {'venue': venue, 'turf': turf, 'bookings': bookings})


