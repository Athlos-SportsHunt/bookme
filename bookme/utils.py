from functools import wraps
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse
from django.conf import settings
from datetime import datetime, timedelta
from core.models import User
from jose import jwt

def login_required(DEV=False):
    def decorator(f):
        @wraps(f)
        def decorated_function(req, *args, **kwargs):
            token = req.COOKIES.get('jwt_token')
            if token:
                if user := get_user_from_token(token):
                    try:
                        user_instance = User.objects.get(id=user)
                        req.user = user_instance
                        return f(req, *args, **kwargs)
                    except User.DoesNotExist:
                        return Response(
                            {"error": "User not found"},
                            status=status.HTTP_404_NOT_FOUND
                        )
            
            if DEV:
                user_instance = User.objects.get(id=2)
                req.user = user_instance
                return f(req, *args, **kwargs)
            
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return decorated_function
    return decorator


def host_required(f):
    @wraps(f)
    @login_required(DEV=True)
    def decorated_function(req, *args, **kwargs):
        if req.user.is_host:
            return f(req, *args, **kwargs)
        return Response(
            {"error": "Only hosts can access this endpoint"},
            status=status.HTTP_403_FORBIDDEN
        )
    return decorated_function


def login_handler(req):
    # Generate JWT
    payload = {
        'user_id': req.user.id,
        'exp': datetime.now() + timedelta(days=10)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')
    
    # Redirect to frontend with token
    frontend_url = settings.FRONTEND_URL[0]
    response = HttpResponseRedirect(f"{frontend_url}")
    
    # Set JWT as cookie
    response.set_cookie(    
        'jwt_token', 
        token,
        httponly=True, 
        secure=True,
        samesite='None'
    )
    
    return response


def get_user_from_token(token):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=['HS256'],
        )
        return payload.get('user_id')
    
    except jwt.ExpiredSignatureError:
        # Token is expired
        return None
    
    except jwt.InvalidTokenError as e:
        # Token is invalid
        print(f"Invalid token: {str(e)}")  # Optional: remove in production
        return None

def logout_handler(req):
    frontend_url = settings.FRONTEND_URL[0]
    response = HttpResponseRedirect(f"{frontend_url}")
    
    # Remove JWT as cookie
    response.delete_cookie('jwt_token')
    
    return response