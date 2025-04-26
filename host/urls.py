from django.urls import path
from .views import *

urlpatterns = [
    path('venues/', host_venues, name='host-venues'),
    path('venues/create/', create_venue, name='create-venue'),
    path('venues/<int:venue_id>/turfs/create/', create_turf, name='create-turf'),
    path('offline-booking/', offline_slot_booking, name='offline-booking'),
    path('bookings/', host_bookings, name='host-bookings'),
    path('venue/<int:venue_id>/bookings/', venue_bookings, name='host-venue-turfs'),
    path('turf/<int:turf_id>/bookings/', turf_bookings, name='host-turf-bookings'),
    path('recent-bookings/', recent_bookings, name='recent-bookings'),
]