from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from bookme.utils import host_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Sport, Venue, Turf, Booking
from .serializers import (
    CreateVenueSerializer, CreateTurfSerializer, VenueSerializer, 
    TurfSerializer, OfflineBookingSerializer, BookingDetailsSerializer
)

@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('Success', VenueSerializer(many=True)),
        401: openapi.Response('Unauthori    zed - Invalid or missing token'),
        403: openapi.Response('Forbidden - User is not a host')
    },
    operation_description="""List all venues and their turfs owned by the requesting host.
    Returns a list of venues with their associated turfs, sports, and pricing information."""
)
@api_view(['GET'])
@host_required
def host_venues(request):
    venues = Venue.objects.filter(host=request.user)
    serializer = VenueSerializer(venues, many=True)
    print(serializer.data)
    return Response(serializer.data)

@swagger_auto_schema(
    method='post',
    request_body=CreateVenueSerializer,
    responses={
        201: openapi.Response('Created', VenueSerializer),
        400: openapi.Response('Bad Request', examples={'application/json': {
            'name': ['This field is required'],
            'turfs': [
                {
                    'name': ['This field is required'],
                    'sports': ['At least one sport is required'],
                    'price_per_hr': ['Must be greater than 0']
                }
            ],
            'error': 'Validation error message'
        }}),
        401: openapi.Response('Unauthorized - Invalid or missing token'),
        403: openapi.Response('Forbidden - User is not a host')
    },
    operation_description="""
    Create a new venue with optional turfs.
    
    Required fields:
    - name: Venue name (must be unique)
    
    Optional fields:
    - turfs: List of turfs to create with the venue, each containing:
        - name: Turf name (must be unique within venue)
        - sports: List of sport IDs
        - price_per_hr: Price per hour (decimal > 0)
    """
)
@api_view(['POST'])
@host_required
def create_venue(request):
    try:
        serializer = CreateVenueSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        venue = serializer.save(host=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error creating venue: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred while creating the venue'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='post',
    request_body=CreateTurfSerializer,
    responses={
        201: openapi.Response('Created', TurfSerializer),
        400: openapi.Response('Bad Request', examples={'application/json': {
            'name': ['This field is required'],
            'sports': ['At least one sport is required'],
            'price_per_hr': ['Must be greater than 0'],
            'error': 'Validation error message'
        }}),
        401: openapi.Response('Unauthorized - Invalid or missing token'),
        403: openapi.Response('Forbidden - Not venue owner'),
        404: openapi.Response('Not Found - Venue does not exist')
    },
    operation_description="""
    Add a new turf to an existing venue.
    
    Required fields:
    - name: Turf name (must be unique within venue)
    - sports: List of sport IDs
    - price_per_hr: Price per hour (decimal > 0)
    """
)
@api_view(['POST'])
@host_required # owner required
def create_turf(request, venue_id):
    try:
        venue = get_object_or_404(Venue, id=venue_id, host=request.user)

        needed_data = {}
        try:
            needed_data["name"] = request.data['name']
            try:
                sport = Sport.objects.get(Q(name__iexact=request.data["sport_type"]))
            except Sport.DoesNotExist:
                return Response({'error': f'Sport {request.data["sport_type"]} does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            
            needed_data["sports"] = [sport.id]
            needed_data["price_per_hr"] = request.data["price_per_hr"]
        
        except Exception as e :
            return Response(e, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        serializer = CreateTurfSerializer(data=needed_data, context={'venue': venue})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        turf = serializer.save(venue=venue)
        response_serializer = TurfSerializer(turf)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error creating turf: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred while creating the turf'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    request_body=OfflineBookingSerializer,
    responses={
        201: openapi.Response('Created', examples={'application/json': {
            'message': 'Offline slot booking created successfully!',
            'booking_id': 1,
            'start_time': '2025-04-06T14:00:00Z',
            'end_time': '2025-04-06T15:00:00Z',
            'turf': 'Turf Name',
            'venue': 'Venue Name'
        }}),
        400: openapi.Response('Bad Request', examples={'application/json': {
            'venue_id': ['Invalid venue'],
            'turf_id': ['Invalid turf for this venue'],
            'start_date': ['Invalid date format'],
            'duration': ['Must be at least 60 minutes and in increments of 30 minutes'],
            'error': 'This time slot overlaps with an existing booking'
        }}),
        401: openapi.Response('Unauthorized - Invalid or missing token'),
        403: openapi.Response('Forbidden - Not venue owner')
    },
    operation_description="""
    Create an offline booking slot for a turf. Only accessible by the host of the venue.
    
    Required fields:
    - venue_id: ID of the venue
    - turf_id: ID of the turf
    - start_date: Start datetime in ISO format (YYYY-MM-DDTHH:MM)
    - duration: Duration in minutes (minimum 60, must be in increments of 30)
    """
)
@api_view(['POST'])
@host_required
def offline_slot_booking(request):
    serializer = OfflineBookingSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        try:
            booking = serializer.save()
            return Response({
                'message': 'Offline slot booking created successfully!',
                'booking_id': booking.id,
                'start_time': booking.start_datetime,
                'end_time': booking.end_datetime,
                'turf': booking.turf.name,
                'venue': booking.turf.venue.name
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error creating offline booking: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred while creating the booking'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'days', openapi.IN_QUERY,
            description='Number of days to look back (default: 7)',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'venue_id', openapi.IN_QUERY,
            description='Filter bookings by venue ID',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'turf_id', openapi.IN_QUERY,
            description='Filter bookings by turf ID',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
    ],
    responses={
        200: openapi.Response('Success', BookingDetailsSerializer(many=True)),
        400: openapi.Response('Bad Request', examples={'application/json': {
            'error': 'Invalid venue_id or turf_id'
        }}),
        401: openapi.Response('Unauthorized - Invalid or missing token'),
        403: openapi.Response('Forbidden - User is not a host')
    },
    operation_description="""List recent bookings for the host's venues/turfs.
    
    Optional query parameters:
    - days: Number of days to look back (default: 7)
    - venue_id: Filter bookings by venue ID
    - turf_id: Filter bookings by turf ID
    
    Returns a list of bookings with user details, turf information, and booking times."""
)
@api_view(['GET'])
@host_required
def host_bookings(request):
    try:
        # Get query parameters
        days = int(request.query_params.get('days', 7))
        venue_id = request.query_params.get('venue_id')
        turf_id = request.query_params.get('turf_id')
        
        # Base query: get bookings for turfs owned by the host
        lookback_date = timezone.now() - timedelta(days=days)
        query = Q(turf__venue__host=request.user) & Q(start_datetime__gte=lookback_date)
        
        # Apply filters if provided
        if venue_id:
            venue = get_object_or_404(Venue, id=venue_id, host=request.user)
            query &= Q(turf__venue=venue)
        
        if turf_id:
            turf = get_object_or_404(Turf, id=turf_id, venue__host=request.user)
            query &= Q(turf=turf)
        
        # Get bookings ordered by start time (most recent first)
        bookings = Booking.objects.filter(query).order_by('-start_datetime')
        
        serializer = BookingDetailsSerializer(bookings, many=True)
        return Response(serializer.data)
        
    except ValueError:
        return Response(
            {'error': 'Invalid days parameter'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('Success', BookingDetailsSerializer(many=True)),
        400: openapi.Response('Bad Request', examples={'application/json': {
            'error': 'Invalid turf_id'
        }}),
        401: openapi.Response('Unauthorized - Invalid or missing token'),
        403: openapi.Response('Forbidden - User is not a host')
    },
    operation_description="""List all bookings for a specific turf owned by the host.
    
    Returns a list of bookings with user details, turf information, and booking times."""
)
@api_view(['GET'])
@host_required
def turf_bookings(request, turf_id):
    try:
        turf = get_object_or_404(Turf, id=turf_id, venue__host=request.user)
        bookings = Booking.objects.filter(turf=turf, verified   =True).order_by('-start_datetime')
        
        serializer = BookingDetailsSerializer(bookings, many=True)
        return Response(serializer.data)
        
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error fetching turf bookings: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred while fetching the bookings'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('Success', BookingDetailsSerializer(many=True)),
        400: openapi.Response('Bad Request', examples={'application/json': {
            'error': 'Invalid venue_id'
        }}),
        401: openapi.Response('Unauthorized - Invalid or missing token'),
        403: openapi.Response('Forbidden - User is not a host')
    },
    operation_description="""List all bookings for a specific venue owned by the host.
    
    Returns a list of bookings with user details, turf information, and booking times."""
)
@api_view(['GET'])
@host_required
def venue_bookings(request, venue_id):
    try:
        venue = get_object_or_404(Venue, id=venue_id, host=request.user)
        bookings = Booking.objects.filter(turf__venue=venue, verified=True).order_by('-start_datetime')
        
        serializer = BookingDetailsSerializer(bookings, many=True)
        return Response(serializer.data)
        
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error fetching venue bookings: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred while fetching the bookings'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@api_view(['GET'])
@host_required
def recent_bookings(request):
    bookings = Booking.objects.filter(
        turf__venue__host=request.user,
        verified=True,
    ).order_by('-start_datetime')
    serializer = BookingDetailsSerializer(bookings, many=True)
    return Response(serializer.data)