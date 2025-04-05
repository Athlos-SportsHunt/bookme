from functools import wraps
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import logout
from django.urls import reverse
from django.conf import settings
from datetime import datetime, timedelta
import jwt

def login_handler(req):
    # Generate JWT
    payload = {
        'user_id': req.user.id,
        'exp': datetime.now() + timedelta(days=1)
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
        # Decode the JWT token
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        user_id = payload.get('user_id')
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
def logout_handler(req):
    frontend_url = settings.FRONTEND_URL[0]
    response = HttpResponseRedirect(f"{frontend_url}")
    
    # Remove JWT as cookie
    response.delete_cookie('jwt_token')
    
    return response