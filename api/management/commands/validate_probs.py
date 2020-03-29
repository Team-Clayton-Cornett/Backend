import matplotlib.pyplot as plt
import numpy as np
import os
import time

from django.core.management.base import BaseCommand, CommandError
from datetime import date
# local models
from api.models import Garage, Probability, DayProbability, DAYS_OF_WEEK, Ticket, Park
 
class Command(BaseCommand):
    help = '*Create Help Text*'

    # used to create visualizations for how the probabilities for each garage on each day ...
    # ... match up with the count of tickets for each time interval
    def handle(self, *args, **options):
        garages = Garage.objects.all()

        # loop over all garages
        for garage in garages:        
            # loop over all the days
            for day_prob in garage.probability:
                Yprob = np.zeros((96))
                i = 0
                # loop over all the time intervals and get the probability for each
                for prob_interval in day_prob.probability:
                    Yprob[i] = prob_interval.probability * 100
                    i=i+1

                Ycount = np.zeros((96))

                # load ticket dataset
                today = date.today()
                dataset = np.loadtxt('training_data/tickets_' + today.strftime("%m-%d-%Y") +'.csv', delimiter=",", usecols=range(4), skiprows=1)
                
                # get the count of tickets at each time interval
                for row in dataset:
                    if row[3] == 1 and row[2] == garage.id and row[1] == self.convertDay(day_prob.day_of_week):
                        Ycount[int(row[0])] = Ycount[int(row[0])] + 1
                
                X = np.arange(96)

                # plot the count of the tickets as bars
                plt.bar(X, Ycount)
                # plot the probability as line
                plt.plot(X, Yprob, '-r')
                plt.title(garage.name + " " + day_prob.day_of_week)

                # save each figure in validation_images/<day of week>/<garage name>.png
                filename = 'validation_images/'+day_prob.day_of_week+'/' + garage.name + '.png'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                plt.savefig(filename)
                plt.clf()
                plt.close()

                # attempt to bring down cpu usage
                time.sleep(0.01)

    # converts a day to an int
    def convertDay(sef, day_of_week):
        if day_of_week == DAYS_OF_WEEK[0][0] or day_of_week == DAYS_OF_WEEK[0][1]:
            return 6
        elif day_of_week == DAYS_OF_WEEK[1][0] or day_of_week == DAYS_OF_WEEK[1][1]:
            return 0
        elif day_of_week == DAYS_OF_WEEK[2][0] or day_of_week == DAYS_OF_WEEK[2][1]:
            return 1
        elif day_of_week == DAYS_OF_WEEK[3][0] or day_of_week == DAYS_OF_WEEK[3][1]:
            return 2
        elif day_of_week == DAYS_OF_WEEK[4][0] or day_of_week == DAYS_OF_WEEK[4][1]:
            return 3
        elif day_of_week == DAYS_OF_WEEK[5][0] or day_of_week == DAYS_OF_WEEK[5][1]:
            return 4
        elif day_of_week == DAYS_OF_WEEK[6][0] or day_of_week == DAYS_OF_WEEK[6][1]:
            return 5

