from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.urls import path, re_path, include

schema_view = get_schema_view(
    openapi.Info(
        title="Athlos SportsHunt API",
        default_version='v1',
        description="""
        Welcome to the Athlos SportsHunt API documentation. This API provides endpoints for managing sports venues,
        turfs, and bookings.

        ## Authentication
        - All endpoints require JWT authentication unless marked as public
        - Use the Auth0 login endpoints to obtain JWT tokens

        ## Rate Limiting
        - API requests are limited to 100 per hour per user
        - Featured venues and public endpoints have a higher limit
        """,
        terms_of_service="https://www.athlos.com/terms/",
        contact=openapi.Contact(email="contact@athlos.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    patterns=[
        path('', include('core.urls')),
    ],
)
