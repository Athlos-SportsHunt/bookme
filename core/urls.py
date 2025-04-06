from django.urls import path, re_path
from django.conf.urls import include
from . import views
from api_docs import schema_view
from bookme.utils import login_handler, logout_handler

app_name = 'core'

urlpatterns = [
    # API Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Authentication
    path('auth/check/', views.index),
    path("login/", views.login_view, name="login"),
    path("login/handler/", login_handler, name="login_handler"),
    path("logout/", views.logout_view, name="logout"),
    path("logout/handler/", logout_handler, name="logout_handler"),

    # Venue endpoints
    path('venues/', views.venue_list, name='venue-list'),
    path('venues/<int:venue_id>/', views.venue_detail, name='venue-detail'),
    path('orders/create/', views.create_order, name='create-order'),
    path('venues/featured/', views.featured_venues, name='featured-venues'),
    path('venues/filter/', views.filter_venues, name='filter-venues'),
]

app_name = "core"