from django.urls import path
from .views import *
from bookme.utils import login_handler, logout_handler

urlpatterns = [
    path('auth/check/', index),
    path("login/", login_view, name="login"),
    path("login/handler/", login_handler, name="login_handler"),
    path("logout/", logout_view, name="logout"),
    path("logout/handler/", logout_handler, name="logout_handler"),
    # Venue endpoints
    path('venues/', venue_list, name='venue-list'),
    path('venue/<int:venue_id>/', venue_detail, name='venue-detail'),
    path('venues/featured/', featured_venues, name='featured-venues'),
    path('venues/filter/', filter_venues, name='filter-venues'),
]

app_name = "core"