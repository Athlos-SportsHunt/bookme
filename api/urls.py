from django.urls import path
from .views import *

urlpatterns = [
    path("handle_booking/", create_slot_order, name="handle_booking"),
]

app_name = 'api'