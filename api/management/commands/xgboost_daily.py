import csv
import math
import json
import numpy as np
import os

from django.core.management.base import BaseCommand, CommandError
from xgboost import XGBClassifier
from datetime import date
from enum import IntEnum 
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# local models
from api.models import Garage, Probability, DayProbability, DAYS_OF_WEEK, Ticket, Park

class WasTicketed(IntEnum):
    NO = 0
    YES = 1

# Designed to be run once daily 
# Loads and formats training data into .csv for processing and redundancy
# Attempts to recalibrate model based on new ticket data
# Updates the ticketing probabilities in the DB


# Example Crontab command (everyday at 1:00 AM):
# 0 1  * * * cd <project root> &&  <project root>/venv/bin/python <project root>/manage.py xgboost_daily >> <cron output location> 2>&1

class Command(BaseCommand):
    help = '*Create Help Text*'

    def handle(self, *args, **options):
        # lead today's training data
        self.load_csv()

        # load today's data
        today = date.today()
        dataset = np.loadtxt('training_data/tickets_' + today.strftime("%m-%d-%Y") +'.csv', delimiter=",", usecols=range(4), skiprows=1)
        
        # split data into X and y
        X = dataset[:,0:3]
        Y = dataset[:,3]

        # fit model
        model = XGBClassifier()
        model.fit(X, Y)

        # use updated model to write new probabilites for each time interval to the DB
        self.write_probabilities_to_database(model)

        self.stdout.write('The xgboost_daily task was ran at ' + str(today))

    # writes new probabilities to DB, based on the newly updated model
    def write_probabilities_to_database(self, model):
        # get all garages
        queryset = Garage.objects.all()

        # there are 51744 probabilites to write (7 days * 77 garages * 96 intervals in the day)
        X_test = np.zeros((51744,3))
        inx = 0
        # init the input dataset that we are going to use the model to predict on
        for i in range(77):
            for j in range(7):
                for k in range(96):
                    # time interval
                    X_test[inx][0] = k
                    # day of week
                    X_test[inx][1] = j
                    # garage
                    X_test[inx][2] = i
                    inx = inx + 1

        # output is the probabilites for each time interval
        preds = model.predict_proba(X_test)

        i=0
        # loop over all garages in DB and update with the new probabilites
        for garage in queryset:
            garage_probs_new = []
            for garage_day_prob in garage.probability:
                day_probs_new = []
                for garage_interval_prob in garage_day_prob.probability:
                    garage_interval_prob.probability = preds[i][1]
                    i=i+1
                    day_probs_new.append(garage_interval_prob)
                garage_day_prob.probability = day_probs_new
                garage_probs_new.append(garage_day_prob)
            # overwrite old probabiliy list
            garage.probability = garage_probs_new
            
            if garage and garage_probs_new:
                garage.save()

    # outputs probs to a file
    def output_probs(self, model):
        X_test = np.zeros((51744,3))
        inx = 0
        for i in range(77):
            for j in range(7):
                for k in range(96):
                    X_test[inx][0] = k
                    X_test[inx][1] = j
                    X_test[inx][2] = i
                    inx = inx + 1

        preds = model.predict_proba(X_test)

        with open("training_data/pred.txt", "w") as file:
            np.savetxt(file, preds)
                      


    # Creates /opt/capstone/training_data/tickets<date>.csv with relevent training data from current DB state
    def load_csv(self):
        # A daily copy is kept, named by day
        today = date.today()

        # just in case training_data dir does not exist yet
        filename = 'training_data/tickets_' + today.strftime("%m-%d-%Y") +'.csv'
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        training_set = open((filename), 'w', newline='')

        # the data we are training on
        writer = csv.writer(training_set)
        writer.writerow(['time','day_of_week', 'garage', 'ticketed'])

        # gets all parks that do have a ticket
        parksTicketed = Park.objects.exclude(ticket = None).exclude(end = None)

        for park in parksTicketed:
            startTime = park.start
            endTime = park.end
            # the int representation of a garage
            garage = park.garage.id
            # the time the park recieved a ticket
            dateTimeTicketed = park.ticket.date 

            # gets 15 minute time interval offset
            startOffset = math.floor(((startTime.hour * 60) + startTime.minute)/15)
            endOffset = math.floor(((endTime.hour * 60) + endTime.minute)/15)
            
            # this is the 15 minute time interval in which the park recieved a ticket
            ticketOffset = math.floor(((dateTimeTicketed.hour * 60) + dateTimeTicketed.minute)/15)

            # the int representation of a weekday
            dayCode = dateTimeTicketed.weekday()

            # ticket the time interval of ticketing, otherwise create a non ticket event
            for i in range(startOffset, endOffset + 1):
                if(i == ticketOffset): 
                    writer.writerow((i, dayCode, garage, int(WasTicketed.YES)))
                else:
                    writer.writerow((i, dayCode, garage, int(WasTicketed.NO)))

        # gets all parks that did not result in a ticket
        parksNotTicketed = Park.objects.filter(ticket = None).exclude(end = None)

        for park in parksNotTicketed:
            startTime = park.start
            endTime = park.end
            # the int representation of a garage
            garage = park.garage.id

            # gets 15 minute time interval offset
            startOffset = math.floor(((startTime.hour * 60) + startTime.minute)/15)
            endOffset = math.floor(((endTime.hour * 60) + endTime.minute)/15)

            # the int representation of a weekday
            dayCode = dateTimeTicketed.weekday()

            # there will always be not ticket events
            for i in range(startOffset, endOffset + 1):
                writer.writerow((i, dayCode, garage, int(WasTicketed.NO)))
                