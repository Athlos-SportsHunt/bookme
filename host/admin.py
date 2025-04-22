from django.contrib import admin
from .models import Venue, Turf,Booking

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

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('turf', 'user', 'start_datetime', 'end_datetime', 'total_price', 'is_offline')
    list_filter = ('turf__venue', 'turf', 'is_offline')
    search_fields = ('turf__name', 'user__username', 'turf__venue__name')
    readonly_fields = ('total_price',)

    def get_queryset(self, request):
        # If superuser, show all bookings
        # If host, show only bookings for their turfs
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(turf__venue__host=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Limit turf choices to only those owned by the current user
        if db_field.name == "turf" and not request.user.is_superuser:
            kwargs["queryset"] = Turf.objects.filter(venue__host=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
