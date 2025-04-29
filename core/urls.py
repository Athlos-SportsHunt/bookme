from django.conf import settings
from django.urls import path, re_path
from bookme.utils import login_handler, logout_handler
from .views import *
from api_docs import schema_view

app_name = 'core'
urlpatterns = [
    # Authentication
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
    
    # order endpoints
    path('orders/create/', create_order, name='create-order'),
    path('orders/checkout/', checkout, name='checkout'),

    # My Bookings
    path('my-bookings/', my_bookings, name='my-bookings'),
]


if settings.DEBUG:
    urlpatterns += [
        # API Documentation
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    ]
app_name = "core"