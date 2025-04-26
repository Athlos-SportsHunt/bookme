from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from bookme.utils import *
from .models import User, Order
from host.models import Venue, Turf, Booking
from .serializers import VenueSerializer, CreateOrderSerializer
import razorpay
from host.serializers import BookingDetailsSerializer

@api_view(['GET'])
def index(req):
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
                    'is_host': user.is_host
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
@swagger_auto_schema(
    operation_description="Get a paginated list of all venues",
    responses={200: VenueSerializer(many=True)}
)
def venue_list(request):
    """Get a paginated list of all venues.

    Returns:
        A paginated response containing a list of venues.
        Each page contains 10 venues.
    """
    paginator = PageNumberPagination()
    paginator.page_size = 10  # Show 10 venues per page
    
    venues = Venue.objects.all()
    result_page = paginator.paginate_queryset(venues, request)
    
    serializer = VenueSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@swagger_auto_schema(
    operation_description="Get detailed information about a specific venue",
    responses={
        200: VenueSerializer(),
        404: 'Venue not found'
    }
)
def venue_detail(request, venue_id):
    """Get detailed information about a specific venue.

    Args:
        venue_id (int): The ID of the venue to retrieve

    Returns:
        Detailed venue information including all turfs.

    Raises:
        404: If the venue is not found
    """
    venue = get_object_or_404(Venue, id=venue_id)
    serializer = VenueSerializer(venue)
    return Response(serializer.data)

@api_view(['GET'])
@swagger_auto_schema(
    operation_description="Get the 3 most recently added venues",
    responses={200: VenueSerializer(many=True)}
)
def featured_venues(request):
    """Get the 3 most recently added venues.

    This endpoint returns the newest venues on the platform,
    useful for highlighting new additions to users.

    Returns:
        List of the 3 most recently added venues with their details.
    """
    venues = Venue.objects.all().order_by('-id')[:3]  # Get last 3 venues by ID
    serializer = VenueSerializer(venues, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@swagger_auto_schema(
    operation_description="Filter venues by various criteria",
    manual_parameters=[
        openapi.Parameter('name', openapi.IN_QUERY, description="Filter venues by name (case-insensitive)", type=openapi.TYPE_STRING),
        openapi.Parameter('sports', openapi.IN_QUERY, description="Filter by sports (comma-separated list)", type=openapi.TYPE_STRING),
        openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price per hour", type=openapi.TYPE_NUMBER),
        openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price per hour", type=openapi.TYPE_NUMBER)
    ],
    responses={200: VenueSerializer(many=True)}
)
def filter_venues(request):
    """Filter venues based on multiple criteria.

    Filter venues by name, sports offered, and price range of turfs.
    All filter parameters are optional.

    Query Parameters:
        name (str, optional): Filter venues by name (case-insensitive partial match)
        sports (str, optional): Comma-separated list of sports (e.g., 'football,cricket')
        min_price (decimal, optional): Minimum price per hour for turfs
        max_price (decimal, optional): Maximum price per hour for turfs

    Returns:
        Paginated list of venues matching the filter criteria
    """
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
        sport_list = [s.strip() for s in sports.split(',') if s.strip()]
        if sport_list:
            query = Q()
            for sport in sport_list:
                query |= Q(turfs__sports__name__iexact=sport)
            venues = venues.filter(query).distinct()
    
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


@swagger_auto_schema(
    method='post',
    request_body=CreateOrderSerializer,
    responses={
        201: openapi.Response('Created', examples={'application/json': {
            'message': 'Order created successfully!',
            'order_id': 'order_123xyz',
            'amount': 100000,  # in paise
            'currency': 'INR',
            'key_id': 'rzp_test_xxx',
            'booking_details': {
                'turf': 'Turf Name',
                'venue': 'Venue Name',
                'start_time': '2025-04-07T10:00:00+05:30',
                'end_time': '2025-04-07T11:00:00+05:30',
                'duration': '60 minutes'
            }
        }}),
        400: openapi.Response('Bad Request', examples={'application/json': {
            'venue_id': ['Invalid venue'],
            'turf_id': ['Invalid turf for this venue'],
            'start_date': ['Invalid date format or slot unavailable'],
            'duration': ['Must be at least 60 minutes and in increments of 30 minutes']
        }}),
        401: openapi.Response('Unauthorized - Invalid or missing token')
    },
    operation_description="""
    Create a new order for a turf booking.
    
    Required fields:
    - venue_id: ID of the venue
    - turf_id: ID of the turf
    - start_date: Start datetime in ISO format (YYYY-MM-DDTHH:MM)
    - duration: Duration in minutes (minimum 60, must be in increments of 30)
    """
)
@api_view(['POST'])
@login_required()
def create_order(request):
    """Create a new order for a turf booking."""
    serializer = CreateOrderSerializer(data=request.data)
    if serializer.is_valid():
        try:
            validated_data = serializer.validated_data
            turf = validated_data['turf']
            razorpay_order = validated_data['razorpay_order']
            
            # Create booking
            booking = Booking.objects.create(
                turf=turf,
                user=request.user,
                start_datetime=validated_data['start_datetime'],
                end_datetime=validated_data['end_datetime'],
                total_price=Decimal(validated_data['amount']) / Decimal(100)  # Convert from paise to rupees
            )
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                booking=booking,
                order_id=razorpay_order['id'],
                amount=Decimal(validated_data['amount']) / Decimal(100)  # Convert from paise to rupees
            )
            
            return Response({
                'message': 'Order created successfully!',
                'order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'key_id': settings.RAZORPAY_KEY_ID,
                'booking_details': {
                    'turf': turf.name,
                    'venue': turf.venue.name,
                    'start_time': validated_data['start_datetime'].isoformat(),
                    'end_time': validated_data['end_datetime'].isoformat(),
                    'duration': f"{validated_data['duration']} minutes"
                }
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error creating order: {str(e)}")
            # If there was an error, clean up any created objects
            if 'booking' in locals():
                booking.delete()
            return Response(
                {'error': 'An unexpected error occurred while creating the order'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def checkout(request):
    """
    Handle Razorpay payment callback and verify payment signature.
    And handle rhe booking.
    """
    # Extract required Razorpay payment parameters from request data
    payment_id = request.data.get('razorpay_payment_id')
    razorpay_order_id = request.data.get('razorpay_order_id')
    signature = request.data.get('razorpay_signature')

    # Ensure all required values are present
    if not all([payment_id, razorpay_order_id, signature]):
        return Response(
            {'error': 'Missing required payment parameters.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }
    
    if not Order.objects.filter(order_id=razorpay_order_id).exists():
        return Response(
            {'error': "Order doesn't exists."},
            status=status.HTTP_400_BAD_REQUEST
        )

    order = Order.objects.get(order_id=razorpay_order_id)
    
    # Verify payment signature using Razorpay SDK
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
    try:
        result = client.utility.verify_payment_signature(params_dict)
        
        if result is None:
            return Response(
                {'error': 'Payment verification failed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.payment_id = payment_id
        order.signature = signature
        order.save()
        
        order.booking.verified = True
        order.booking.save()
        
        return Response(
            {'message': 'Payment verified successfully!'},
            status=status.HTTP_200_OK
        )

    except razorpay.errors.SignatureVerificationError:
        return Response({'error': 'Invalid payment signature'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@login_required()
def my_bookings(request):
    """
    Get all bookings for the authenticated user.
    Returns a list of bookings with turf and venue details.
    """
    bookings = Booking.objects.filter(user=request.user, verified=True).order_by('-start_datetime')
    serializer = BookingDetailsSerializer(bookings, many=True)
    return Response(serializer.data)
