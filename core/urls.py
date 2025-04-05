from django.urls import path
from .views import *
from bookme.utils import login_handler, logout_handler

urlpatterns = [
    path('auth/check/', index),
    path("login/", login_view, name="login"),
    path("login/handler/", login_handler, name="login_handler"),
    path("logout/", logout_view, name="logout"),
    path("logout/handler/", logout_handler, name="logout_handler"),
]

app_name = "core"