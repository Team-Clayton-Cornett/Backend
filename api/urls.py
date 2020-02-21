"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Django Imports
from django.contrib import admin
from django.urls import path, include

# Third-Party Imports
from rest_framework.authtoken.views import obtain_auth_token

# Local Imports
from . import views
from . import viewsets

# definitions for viewsets
garage_list = viewsets.GarageViewSet.as_view({
    'get': 'list'
})

garage_detail = viewsets.GarageViewSet.as_view({
    'get': 'retrieve'
})

user_detail = viewsets.UserViewSet.as_view({
    'get': 'get_user',
    'post': 'create_user',
    'patch': 'update_user'
})

user_unassigned_tickets = viewsets.TicketViewSet.as_view({
    'get': 'get_user_unassigned_tickets'
})

ticket_detail = viewsets.TicketViewSet.as_view({
    'post': 'create_user_ticket',
    'patch': 'create_user_ticket'
})

park_detail = viewsets.ParkViewSet.as_view({
    'get': 'get_user_parks',
    'post': 'create_user_park',
    'patch': 'update_user_park'
})

password_reset_create = viewsets.PasswordResetViewSet.as_view({
    'post': 'generate_password_reset_token'
})

password_reset_validate_token = viewsets.PasswordResetViewSet.as_view({
    'post': 'validate_password_reset_token'
})

password_reset_reset = viewsets.PasswordResetViewSet.as_view({
    'post': 'reset_password'
})

urlpatterns = [
    path('login/', obtain_auth_token, name='api_login'),
    path('user/', user_detail, name='user'),
    path('user/password_reset/create/', password_reset_create, name='user_password_reset_create'),
    path('user/password_reset/validate_token/', password_reset_validate_token, name='user_password_reset_validate_token'),
    path('user/password_reset/reset/', password_reset_reset, name='user_password_reset_reset'),
    path('user/ticket/', ticket_detail, name='ticket'),
    path('user/tickets/unassigned', user_unassigned_tickets, name='user_unassigned_tickets'),
    path('user/park/', park_detail, name='park'),
    path('garages/', garage_list, name='garage_list'),
    path('garages/<str:day_of_week>/', garage_list, name='garage_list_day_of_week'),
    path('garages/<str:day_of_week>/<str:time>/', garage_list, name='garage_list_day_of_week'),
    path('garage/<int:pk>/', garage_detail, name='garage_detail'),
    path('garage/<int:pk>/<str:day_of_week>/', garage_detail, name='garage_detail'),
    path('garage/<int:pk>/<str:day_of_week>/<str:time>/', garage_detail, name='garage_detail')
]
