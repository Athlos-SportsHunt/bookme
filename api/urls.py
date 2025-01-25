from django.urls import path
from .views import *

urlpatterns = [
    path("handle_booking/", create_slot_order, name="handle_booking"),
    path("venues/", create_venue, name="create_venue"),
    path("venues/<int:venue_id>/turf/", create_turf, name="create_turf"),
    path('offline-slot-booking/', offline_slot_booking, name='offline_slot_booking'),
]

app_name = 'api'
