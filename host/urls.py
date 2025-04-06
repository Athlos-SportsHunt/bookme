from django.urls import path
from .views import create_venue, create_turf, offline_slot_booking

urlpatterns = [
    path('venues/create/', create_venue, name='create-venue'),
    path('venues/<int:venue_id>/turfs/create/', create_turf, name='create-turf'),
    path('offline-booking/', offline_slot_booking, name='offline-booking'),
]