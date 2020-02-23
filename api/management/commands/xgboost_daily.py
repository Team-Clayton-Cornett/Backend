import csv
import math

from django.core.management.base import BaseCommand, CommandError
from numpy import loadtxt
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
class Command(BaseCommand):
    help = '*Create Help Text*'

    def handle(self, *args, **options):
        # lead today's training data
        self.load_csv()

        # load data
        dataset = loadtxt('training_data/tickets_02-22-2020.csv', delimiter=",", usecols=range(4), skiprows=1)
        # split data into X and y
        X = dataset[:,0:3]
        Y = dataset[:,3]
        # split data into train and test sets
        seed = 1
        test_size = 0.33
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)
        # fit model no training data
        model = XGBClassifier()
        model.fit(X_train, y_train)

        # make predictions for test data
        
        print(X_test)

        y_pred = model.predict(X_test)

        print(y_pred)
        predictions = [round(value) for value in y_pred]
        # evaluate predictions
        accuracy = accuracy_score(y_test, predictions)
        print("Accuracy: %.2f%%" % (accuracy * 100.0))

        self.stdout.write('The xgboost_daily task was ran.')

    # Creates /opt/capstone/training_data/tickets<date>.csv with relevent training data from current DB state
    def load_csv(self):
        # A daily copy is kept, named by day
        today = date.today()
        training_set = open(('training_data/tickets_' + today.strftime("%m-%d-%Y") +'.csv'), 'w', newline='')

        writer = csv.writer(training_set)
        writer.writerow(['time','day_of_week', 'garage', 'ticketed'])

        parksTicketed = Park.objects.exclude(ticket = None).exclude(end = None)

        for park in parksTicketed:
            startTime = park.start
            endTime = park.end
            garage = park.garage.id
            dateTimeTicketed = park.ticket.date

            startOffset = math.floor(((startTime.hour * 60) + startTime.minute)/15)
            endOffset = math.floor(((endTime.hour * 60) + endTime.minute)/15)
            ticketOffset = math.floor(((dateTimeTicketed.hour * 60) + dateTimeTicketed.minute)/15)

            dayCode = dateTimeTicketed.weekday()

            for i in range(startOffset, endOffset + 1):
                if(i == ticketOffset): 
                    writer.writerow((i, dayCode, garage, int(WasTicketed.YES)))
                else:
                    writer.writerow((i, dayCode, garage, int(WasTicketed.NO)))

        parksNotTicketed = Park.objects.filter(ticket = None).exclude(end = None)

        for park in parksNotTicketed:
            startTime = park.start
            endTime = park.end
            garage = park.garage.id

            startOffset = math.floor(((startTime.hour * 60) + startTime.minute)/15)
            endOffset = math.floor(((endTime.hour * 60) + endTime.minute)/15)

            dayCode = dateTimeTicketed.weekday()

            for i in range(startOffset, endOffset + 1):
                writer.writerow((i, dayCode, garage, int(WasTicketed.NO)))
                