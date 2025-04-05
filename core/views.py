from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.contrib.auth import logout
from django.urls import reverse
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from bookme.utils import get_user_from_token
from .models import User
from host.models import Venue
from .serializers import VenueSerializer

@api_view(['GET'])
def index(req):
    print(req.user)
    token = req.COOKIES.get('jwt_token')
    if token:
        if user := get_user_from_token(token):

            user = User.objects.get(id=user)
            return Response({
                'isAuthenticated': True,
                'user': {
                    'id': user.id,
                    'name': user.username,
                    'email': user.email,
                    'is_org': user.is_organizer
                }
            })
    return Response({
        'isAuthenticated': False
    })

def login_view(req):
    return HttpResponseRedirect(reverse('social:begin', args=['auth0']))

def logout_view(req):
    logout(req)
    
    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
    return_to = req.build_absolute_uri(reverse('core:logout_handler'))

    return HttpResponseRedirect(f"https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}")


@api_view(['GET'])
def venue_list(request):
    # Set up pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10  # Show 10 venues per page
    
    venues = Venue.objects.all()
    result_page = paginator.paginate_queryset(venues, request)
    
    serializer = VenueSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def venue_detail(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    serializer = VenueSerializer(venue)
    return Response(serializer.data)

@api_view(['GET'])
def featured_venues(request):
    """Return the 3 most recently added venues"""
    venues = Venue.objects.all().order_by('-id')[:3]  # Get last 3 venues by ID
    serializer = VenueSerializer(venues, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def filter_venues(request):
    """Filter venues based on name, sports, and price range"""
    # Get filter parameters from query string
    name = request.query_params.get('name', '')
    sports = request.query_params.get('sports', '')  # Expect comma-separated sports
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    
    # Start with all venues
    venues = Venue.objects.all()
    
    # Apply filters
    if name:
        venues = venues.filter(name__icontains=name)
    
    if sports:
        # Split the sports string into a list and clean the values
        sport_list = [s.strip().lower() for s in sports.split(',') if s.strip()]
        if sport_list:
            # Filter venues that have turfs with ANY of the specified sports
            venues = venues.filter(turfs__sport__in=sport_list).distinct()
    
    if min_price is not None:
        venues = venues.filter(turfs__price_per_hr__gte=min_price).distinct()
    
    if max_price is not None:
        venues = venues.filter(turfs__price_per_hr__lte=max_price).distinct()
    
    # Set up pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(venues, request)
    
    serializer = VenueSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)
