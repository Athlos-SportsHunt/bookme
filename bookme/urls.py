
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("core.urls")),
    path("hosts/", include("host.urls")),
    path("", include('social_django.urls', namespace='social')),
    path('admin/', admin.site.urls),
]
