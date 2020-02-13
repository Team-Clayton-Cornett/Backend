import csv
import math

from django.core.management.base import BaseCommand, CommandError
from numpy import loadtxt
from xgboost import XGBClassifier
from datetime import date
from enum import Enum 

# local models
from api.models import Garage, Probability, DayProbability, DAYS_OF_WEEK, Ticket

# Designed to be run once daily 
# Loads and formats training data into .csv for processing and redundancy
# Attempts to recalibrate model based on new ticket data
# Updates the ticketing probabilities in the DB
class Command(BaseCommand):
    help = '*Create Help Text*'

    def handle(self, *args, **options):
        # lead today's training data
        self.load_csv()

        self.stdout.write('The xgboost_daily task was ran.')

    # Creates /opt/capstone/training_data/tickets<date>.csv with relevent training data from current DB state
    def load_csv(self):
        # A daily copy is kept, named by day
        today = date.today()
        training_set = open(('training_data/tickets_' + today.strftime("%m-%d-%Y") +'.csv'), 'w', newline='')

        writer = csv.writer(training_set)
        writer.writerow(['time','day_of_week', 'garage', 'ticketed'])

        # As of right now, all ticket data is pulled from DB
        tickets = Ticket.objects.all().values_list('date','day_of_week', 'garage')
        for ticket in tickets:
            newTime = ticket[0].time().replace(second=0, microsecond=0)
            # Calculate the 15 minute offset from 00:00, based on the time of ticketing
            intervalOffset = newTime.hour*60 + newTime.minute
            intervalOffset = math.floor(intervalOffset/15)   

            # 4 features to train on: 15-min offset, day of week, garage id, ticketed or not (bool)
            ticketT = (intervalOffset, ticket[1], ticket[2], 1)
            
            writer.writerow(ticketT)
