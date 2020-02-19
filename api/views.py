# REST Framework: https://www.django-rest-framework.org/
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import datetime
from random import random

# local models
from api.models import Garage, Probability, DayProbability, Ticket, Park, User

## GENERATE TEST DATA ##

# creates a new park object in the database.
    # date: dateTime object
    # garage: instance of Garage object
    # user: instance of User object. Defaults to None/NULL
def create_park(start, end, ticket, garage, user):
    Park.objects.create(start=start, end=end, ticket=ticket, garage=garage, user=user)

# create n tickets for each Garage at a random date between start_date and end_date
def create_random_parks(n):
    # Test Data user to be used for creating test/mock data
    user = User.objects.get(first_name='Test Data')
    garages = Garage.objects.all()
    start_date = datetime.datetime(2020,1,1) # January 1, 2020
    end_date = datetime.datetime.now() # The time right now, duh
    date_range = end_date - start_date
    
    for garage in garages:
        for i in range(0,n):
            # initialize random numbers
            random_start = random()
            random_end = random()
            random_ticket = random()
            random_ticket_compare = random()

            # determine start date (random date between 1/1/2020 and time right now)
            start = start_date + random_start * date_range

            # determine end date (random date between start date and 8 hours from then)
            interval_range = start - (start + datetime.timedelta(hours=8))
            end = start + random_end * interval_range

            # default value for ticket (no ticket)
            ticket = None

            # determine whether to create random ticket
            if random_ticket >= random_ticket_compare:
                # determine ticket date (random date between start and end)
                park_range = end - start
                ticket_date = start + random_ticket * park_range

                # create ticket object
                ticket = Ticket(date=ticket_date)

            # create park object
            create_park(start=start, end=end, ticket=ticket, garage=garage, user=user)

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