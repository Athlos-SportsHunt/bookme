from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from bookme.utils import host_required
from django.core.exceptions import ValidationError
from .models import Venue, Turf, Booking
from .serializers import (
    CreateVenueSerializer, CreateTurfSerializer, VenueSerializer, 
    TurfSerializer, OfflineBookingSerializer
)

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
@host_required
def create_turf(request, venue_id):
    try:
        venue = get_object_or_404(Venue, id=venue_id)
        
        # Check if the venue belongs to the requesting host
        if venue.host != request.user:
            return Response(
                {'error': 'You do not have permission to add turfs to this venue'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CreateTurfSerializer(data=request.data, context={'venue': venue})
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
