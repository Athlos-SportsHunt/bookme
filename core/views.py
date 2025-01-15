from django.shortcuts import render
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .models import User
from django.contrib.auth import logout 
from django.urls import reverse
from django.conf import settings
from host.models import *

def index(req):
    
    venues = Venue.objects.all()
    return render(req, 'core/pages/index.html', {'venues': venues})

def login_view(req):
    return HttpResponseRedirect(reverse('social:begin', args=['auth0']))

def logout_view(req):
    logout(req)
    
    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
    return_to = req.build_absolute_uri(reverse('index'))
    return HttpResponseRedirect(f"https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}")
    
    
def venue_filter_view(req):
    venue_name = req.GET.get('venue', '')
    print(venue_name, "uhh")
    venues = Venue.objects.filter(name__icontains=venue_name)
    if not venues:
        return render(req, 'core/pages/venue_filter.html', {'error': 'No venues found'})
    return render(req, 'core/pages/venue_filter.html', {'venues': venues})


def venue_view(req, venue_id):
    try:
        venue = Venue.objects.get(id=venue_id)
    except Venue.DoesNotExist:
        return render(req, 'core/pages/venue.html', {'error': 'Venue not found'})
    return render(req, 'core/pages/venue.html', {'venue': venue})


def turf_view(req,venue_id, turf_id):
    try:
        turf = Turf.objects.get(id=turf_id, venue_id=venue_id)
    except Turf.DoesNotExist:
        return render(req, 'core/pages/turf.html', {'error': 'Turf not found'})
    return render(req, 'core/pages/turf.html', {'turf': turf})


def profile_view(req):
    if not req.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    
    bookings = Booking.objects.filter(user=req.user)
    return render(req, 'core/pages/profile.html', {'bookings': bookings})
