from django.urls import path
from .views import *

urlpatterns = [
    path("handle_booking/", handle_booking, name="handle_booking"),
]

app_name = 'api'