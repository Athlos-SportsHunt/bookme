from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name='index'),
    path("login/", login_view, name='login'),
    path("logout/", logout_view, name='logout'),
    path("profile/", profile_view, name='profile'),
    path("venue/", venue_filter_view, name='venue_filter'), #http://127.0.0.1:8000/venue/?venue=test
    path("venue/<int:venue_id>/", venue_view, name='venue'),
    path("venue/<int:venue_id>/turf/<int:turf_id>/", turf_view, name='turf'),
]

app_name = 'core'