# REST Framework: https://www.django-rest-framework.org/
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import datetime
import json
import math
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

# first attempt at creating test data with meaning/trends behind it
def create_structured_parks():
    date = datetime.datetime(2020, 2, 17, 8)
    
    # for now, only create parks on the weekdays
    for i in range (5):
        create_structured_parks_for_day(date)
        date + datetime.timedelta(days=1)

# creates the park data for one day
def create_structured_parks_for_day(day_start):
    user = User.objects.get(first_name='Test Data')
    garages = Garage.objects.all()
    
    # uses the route finder data to try and "intelligently" use possible routes the parking
    # attendents could take

    # for now, three routes / clusters
    num_routes = 3
    routes = []
    # load in the routes from the output route files of route_finder.py command
    for i in range(num_routes):
        routes.append(load_routes("route_visualization/CondensedRoutes/condensed_route_g"+str((i+1))+".json"))

    # constant, just a guess of how long it takes them to patrol a lot 
    time_to_ticket_lot = 7
    # random amount of tickets they give at each lot
    num_tickets = (math.floor(random()*100) % 15) + 1

    # the current time of the patrol
    current_patrol_dt = None
    # time they leave each lot
    leaveTime = []

    # iterate over each route
    for route in routes:
        # start at 8:00am
        current_patrol_dt = day_start

        # iterate over each place in the route, IN ORDER
        for place in route:
            # update the time they visit the lot, add on the time it takes to get between lots
            current_patrol_dt = current_patrol_dt + datetime.timedelta(seconds=(math.floor(place[1])))
            
            # give out tickets at each lot
            for i in range(num_tickets):
                # get the park dates/times based on the current time
                dates = generate_start_end_ticket_dates(current_patrol_dt)
                
                # find the garage object that relates to the current place being enforced in the route
                garageParked = None
                for garage in garages:
                    if(place[0] == garage.name):
                        garageParked = garage

                # create the park in the DB
                create_park(start=dates[0], end=dates[1], ticket=Ticket(date=dates[2]), garage=garageParked, user=user)
            
            # update the current time with the time it takes to ticket a lot
            current_patrol_dt = current_patrol_dt + datetime.timedelta(minutes=time_to_ticket_lot)
        # get the time they leave the last place in the route for each route, 
        # they will restart the route at this time in the next step
        leaveTime.append(current_patrol_dt)

    indx=0

    # for now, I do run the routes a second time, 
    # becuase it ended up finishing each route about halfway through the day
    for route in routes:
        current_patrol_dt = leaveTime[indx]
        for place in route:
            current_patrol_dt = current_patrol_dt + datetime.timedelta(seconds=(math.floor(place[1])))
            for i in range(num_tickets):
                dates = generate_start_end_ticket_dates(current_patrol_dt)
                garageParked = None
                for garage in garages:
                    if(place[0] == garage.name):
                        garageParked = garage
                create_park(start=dates[0], end=dates[1], ticket=Ticket(date=dates[2]), garage=garageParked, user=user)
            current_patrol_dt = current_patrol_dt + datetime.timedelta(minutes=time_to_ticket_lot)
        indx = indx + 1

# generates "random" park start time, end time, and ticket time
def generate_start_end_ticket_dates(date_start):
   # random start/end time within two hours
    offset_start = (math.floor(random()*100)%120) + 10
    offset_end = (math.floor(random()*100)%120) + 10

    park_start = date_start - datetime.timedelta(minutes = offset_start)
    park_end = date_start + datetime.timedelta(minutes = offset_end)

    # ticket it randomly within the start/end time of the park
    ticket_date = date_start + datetime.timedelta(minutes=(math.floor(random()*100) % 10))

    return(park_start, park_end, ticket_date)

# loads the routes from file as array
def load_routes(filename):
    with open(filename) as f:
        route_array = json.load(f)
        return route_array


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