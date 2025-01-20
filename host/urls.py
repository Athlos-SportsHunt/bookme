from django.urls import path
from .views import *
urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('venue/<int:venue_id>/', venue, name='venue'),
    path('create_venue/', create_venue, name='create_venue'),
    path('venue/<int:venue_id>/create_turf', create_turf, name='create_turf'),
]

app_name = 'host'