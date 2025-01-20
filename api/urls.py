from django.urls import path
from .views import *

urlpatterns = [
    path("handle_booking/", create_slot_order, name="handle_booking"),
    path("venues/", create_venue, name="create_venue"),
    path("venues/<int:venue_id>/turf/", create_turf, name="create_turf"),
]

app_name = 'api'