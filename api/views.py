# REST Framework: https://www.django-rest-framework.org/
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import datetime
import json
import math
from random import random
from random import randrange
from random import randint
import pickle

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

# start it off!
def create_parks_v2():
    create_parks_updated(park_percent_thresh=35, park_ticket_percent_thresh=98, park_max_time=240, park_min_time=10, parks_per_iteration=1)

# second attempt at creating meaningful park data that contains trends
def create_parks_updated(park_percent_thresh, park_ticket_percent_thresh, park_max_time, park_min_time, parks_per_iteration):
    # all parks will be added under the test user
    user = User.objects.get(first_name='Test Data')
    garages = Garage.objects.all()

    # for now, enforcement will be done in three routes / clusters
    num_routes = 3
    routes = []
    # load in the routes from the output route files of route_finder.py command
    for i in range(num_routes):
        routes.append(load_routes("route_visualization/CondensedRoutes/condensed_route_g"+str((i+1))+".json"))

    # today, set to 7:00 (begin patrol time)
    date = datetime.datetime.now()
    date = date.replace(hour=7, minute=0, second=0, microsecond=0)

    # get the list of times that each lot is patrolled
    patrol_times = []
    for route in routes:
        patrol_times.append(get_patrol_times_list(patrol_time_start=date, patrol_time_end=(date+datetime.timedelta(minutes=660)), patrol_lot_time_min=5, patrol_lot_time_max=15, patrol_route=route))

    # add previous 15 days to the queue for ticket generation
    dates = []
    for i in range(1,15):
        dates.append(date - datetime.timedelta(days=i))

    # iterate over the past 15 days
    for date in dates:
        # random start time within 0-45 minutes of 7:00 am
        date_begin = date + datetime.timedelta(minutes=randrange(0, 45, 1))
        # iterate over each 5 minute time interval in the enforcement hours (7:00am - 6:00pm)
        for current_time_offset in range(0, 660, 5):
            # how many parks pre time interval will be attempted in each garage
            for i in range(parks_per_iteration):
                # set the start time of the park
                park_start_time = date_begin + datetime.timedelta(minutes=current_time_offset)
                # set the length of the park
                park_length = randrange(park_min_time, park_max_time, 1)
                # set when the park will end
                park_end_time = park_start_time + datetime.timedelta(minutes=park_length)

                # iterate over all garages
                for garage in garages:
                    # decide wether or not to generate a park
                    park_prob = random() * 100
                    if(park_prob > park_percent_thresh):
                        park_made = False                        
                        # only give out tickets on weekdays
                        if date.weekday() < 5:
                            # for each route's patrol times
                            for patrol_time in patrol_times:
                                # for each lot's patrol time
                                for lot_visited in patrol_time:
                                    # if the lot matches the garage name
                                    if lot_visited[0] == garage.name and park_made == False:
                                        # if the park range overlaps the ticketing range, give a ticket
                                        
                                        lot_visited_time1 = lot_visited[1].replace(year=park_start_time.year, month=park_start_time.month, day=park_start_time.day)
                                        lot_visited_time2 = lot_visited[2].replace(year=park_start_time.year, month=park_start_time.month, day=park_start_time.day)

                                        if park_start_time < lot_visited_time1 and park_end_time > lot_visited_time1:
                                            # make sure that the ticket_prob is under the ticketing threshold
                                            ticket_prob = random() * 100
                                            if(ticket_prob < park_ticket_percent_thresh):
                                                create_park(start=park_start_time, end=park_end_time, ticket=Ticket(date=random_date(lot_visited_time1 ,park_end_time)), garage=garage, user=user)
                                                park_made = True
                                        elif lot_visited_time1 < park_start_time and lot_visited_time2 > park_start_time:
                                            ticket_prob = random() * 100
                                            if(ticket_prob < park_ticket_percent_thresh):
                                                create_park(start=park_start_time, end=park_end_time, ticket=Ticket(date=random_date(park_start_time, lot_visited_time2)), garage=garage, user=user)
                                                park_made = True
                                    
                            if park_made == False:
                                # test it again for the threshold, too many parks being created
                                park_prob = random() * 100
                                if(park_prob > park_percent_thresh):
                                    create_park(start=park_start_time, end=park_end_time, ticket=None, garage=garage, user=user)
                            park_made = False

def get_patrol_times_list(patrol_time_start, patrol_time_end ,patrol_lot_time_min, patrol_lot_time_max, patrol_route):
    # current 'time' in the simulation for route patrols (minutes)
    current_time = patrol_time_start

    # array that will hold tuples of (lot_name, lot_patrol_start, lot_patrol_end)
    # the same lot could come up more than once
    patrol_times_for_route = []
    
    # loop the patrol as long as parking is still enforced
    while current_time < patrol_time_end:
        # visit each place along the route
        for place in patrol_route:
            # the time in seconds to get to each lot
            time_to_lot = place[1]
            # lot name
            lot_name = place[0]
            # the time when tickets will start being issued for this lot
            lot_time_start = current_time + datetime.timedelta(seconds=time_to_lot)
            # the time that is spent in this lot giving tickets
            time_in_lot = randrange(patrol_lot_time_min, patrol_lot_time_max, 1)
            # the time when tickets will stop being issued for this lot
            lot_time_end = current_time + datetime.timedelta(minutes=time_in_lot)
            
            # update the current 'time'
            current_time = lot_time_end

            # if the patrol has gone past enforcement hours, reset to the end.
            if(lot_time_end > patrol_time_end):
                lot_time_end = patrol_time_end

            # add the tuple to the list
            patrol_times_for_route.append((lot_name, lot_time_start, lot_time_end))

    return patrol_times_for_route

# first attempt at creating test data with meaning/trends behind it
def create_structured_parks():
    

    date = datetime.datetime.now()
    date = date.replace(hour=7, minute=0, second=0, microsecond=0)

    # add previous 30 days to the queue for ticket generation
    dates = []
    for i in range(1,30):
        dates.append(date - datetime.timedelta(days=i))
    
    # for now, only create parks on the weekdays
    for date in dates:
        create_structured_parks_for_day(date)
        # sprinkle random parks with tickets in there
        #add_random_parks_for_day(date)

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

    # shuffle routes every weekday
    for route in routes:
        weekno = datetime.datetime.today().weekday()
        length = len(route) - 1

        if weekno <5:
            for i in range(weekno):
                route.insert(0,route.pop())


    # constant, just a guess of how long it takes them to patrol a lot 
    time_to_ticket_lot = (math.floor(random()*100) % 7) + 15
    # random amount of tickets they give at each lot
    num_tickets = (math.floor(random()*100) % 15) + 2

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

                # only give tickets out on the weekdays
                weekno = datetime.datetime.today().weekday()
                if weekno<5:
                    # create the park in the DB, with ticket
                    create_park(start=dates[0], end=dates[1], ticket=Ticket(date=dates[2]), garage=garageParked, user=user)
                else:
                    # create the park in the DB, no ticket
                    create_park(start=dates[0], end=dates[1], ticket=None, garage=garageParked, user=user)
            
            # update the current time with the time it takes to ticket a lot
            current_patrol_dt = current_patrol_dt + datetime.timedelta(minutes=time_to_ticket_lot)
            
            # update random time to ticket each lot
            time_to_ticket_lot = (math.floor(random()*100) % 7) + 15

            # updated the random number of tickets to give at each lot
            num_tickets = (math.floor(random()*100) % 15) + 2

        # get the time they leave the last place in the route for each route, 
        # they will restart the route at this time in the next step
        leaveTime.append(current_patrol_dt)

    indx=0

    # for now, I run the routes a second time, 
    # becuase it ended up finishing each route about halfway through the day
    for route in routes:
        current_patrol_dt = leaveTime[indx]
        for place in route:
            current_patrol_dt = current_patrol_dt + datetime.timedelta(seconds=(math.floor(place[1])))
            
            if current_patrol_dt.hour >= 18:
                return

            for i in range(num_tickets):
                dates = generate_start_end_ticket_dates(current_patrol_dt)
                garageParked = None
                for garage in garages:
                    if(place[0] == garage.name):
                        garageParked = garage
                weekno = datetime.datetime.today().weekday()
                if weekno<5:
                    create_park(start=dates[0], end=dates[1], ticket=Ticket(date=dates[2]), garage=garageParked, user=user)
                else:
                    create_park(start=dates[0], end=dates[1], ticket=None, garage=garageParked, user=user)
            current_patrol_dt = current_patrol_dt + datetime.timedelta(minutes=time_to_ticket_lot)
            time_to_ticket_lot = (math.floor(random()*100) % 7) + 15
            num_tickets = (math.floor(random()*100) % 15) + 2
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

# returns a random date between two times
def random_date(start, end):
    rand_date = start + datetime.timedelta(seconds=randint(0, int((end - start).total_seconds())))

    return rand_date

def save_garages():
    garages = Garage.objects.all()

    with(open("tests/garages.dat", "wb")) as file:
        pickle.dump(garages, file)


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