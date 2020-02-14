# REST Framework: https://www.django-rest-framework.org/
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import datetime
import random

# local models
from api.models import Garage, Probability, DayProbability, Ticket, Park

## GENERATE TEST DATA ##

# creates a new ticket object in the database.
    # date: dateTime object
    # garage: instance of Garage object
    # user: instance of User object. Defaults to None/NULL
def create_ticket(date, day_of_week, garage, user=None):
    Ticket.objects.create(date=date, day_of_week=day_of_week, garage=garage, user=user)

# create n tickets for each Garage at a random date between start_date and end_date
def create_random_tickets(n):
    garages = Garage.objects.all()
    start_date = timezone.make_aware(datetime.datetime(2020,1,1)) # January 1, 2020
    end_date = timezone.now() # The time right now, duh
    date_range = end_date - start_date
    
    for garage in garages:
        for i in range(0,n):
            random_num = random.random()
            date = start_date + random_num * date_range
            day_of_week = date.strftime('%a')

            create_ticket(date=date, garage=garage, day_of_week=day_of_week)

"""
Example Class-Based REST View:

class ExampleView(APIView):
    # if authentication is required
    permission_classes = (IsAuthenticated,)

    # for a get method
    def get(self, request):
        # initialize content dictionary
        content = {}

        # perform logic
        # to obtain parameters from GET request
        request.query_params['param_name']

        # return response
        return Response(content)

    # for a POST method
    def post(self, request):
        # initialize content dictionary
        content = {}

        # perform logic
        # to obtain parameters from POST request
        request.data['param_name']

        # return response
        return Response(content)
"""