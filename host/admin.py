from django.contrib import admin
from .models import Venue, Turf

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'host')
    list_filter = ('host',)
    search_fields = ('name', 'host__username')

    def get_queryset(self, request):
        # If superuser, show all venues
        # If host, show only their venues
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(host=request.user)

@admin.register(Turf)
class TurfAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue', 'price_per_hr')
    list_filter = ('venue',)
    search_fields = ('name', 'venue__name')

    def get_queryset(self, request):
        # If superuser, show all turfs
        # If host, show only their turfs
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(venue__host=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Limit venue choices to only those owned by the current user
        if db_field.name == "venue" and not request.user.is_superuser:
            kwargs["queryset"] = Venue.objects.filter(host=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
