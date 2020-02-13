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

urlpatterns = [
    path('hello_world/', views.HelloWorldView.as_view(), name='hello_world'),
    path('login/', obtain_auth_token, name='api_login'),
    path('garages/', garage_list, name='garage_list'),
    path('garages/<str:day_of_week>/', garage_list, name='garage_list_day_of_week'),
    path('garages/<str:day_of_week>/<str:time>/', garage_list, name='garage_list_day_of_week'),
    path('garage/<int:pk>/', garage_detail, name='garage_detail'),
    path('garage/<int:pk>/<str:day_of_week>/', garage_detail, name='garage_detail'),
    path('garage/<int:pk>/<str:day_of_week>/<str:time>/', garage_detail, name='garage_detail')
]
