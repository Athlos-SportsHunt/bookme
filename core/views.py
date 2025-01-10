from django.shortcuts import render
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .models import User
from django.contrib.auth import logout 
from django.urls import reverse
from django.conf import settings

def index(req):
    if req.user.is_authenticated:
        return HttpResponse(f"Hello, {req.user.username}. You're at the core index.")
    return HttpResponse("Hello, world. You're at the core index.")

def login_view(req):
    return HttpResponseRedirect(reverse('social:begin', args=['auth0']))

def logout_view(req):
    logout(req)
    
    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
    return_to = req.build_absolute_uri(reverse('index'))
    return HttpResponseRedirect(f"https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}")
    
    