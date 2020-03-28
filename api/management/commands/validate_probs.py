import matplotlib.pyplot as plt
import numpy as np

from django.core.management.base import BaseCommand, CommandError
from datetime import date
# local models
from api.models import Garage, Probability, DayProbability, DAYS_OF_WEEK, Ticket, Park
 
class Command(BaseCommand):
    help = '*Create Help Text*'

    def handle(self, *args, **options):
        garages = Garage.objects.all()

        probabilities = np.zeros((77, 7, 96))
        garagesList = []

        i=0
        j=0
        k=0
        for garage in garages:
            garagesList.append(garage.name)
            for dayprob in garage.probability:
                for prob in dayprob.probability:
                    probabilities[i][j][k] = prob.probability
                    k=k+1
                j=j+1
                k=0

            i=i+1
            j=0
            k=0
        
        parks = Park.objects.all()
        today = date.today()
        dataset = np.loadtxt('training_data/tickets_' + today.strftime("%m-%d-%Y") +'.csv', delimiter=",", usecols=range(4), skiprows=1)
        ticketsGiven = np.zeros((77, 7, 96), dtype=int)
        for row in dataset:
            if row[3] == 1:
                ticketsGiven[int(row[2])-1][int(row[1])][int(row[0])] = ticketsGiven[int(row[2])-1][int(row[1])][int(row[0])] + 1

        X = np.arange(96)
        Y = np.zeros((96))
        Yprob = np.zeros((96), dtype=float)

        p = 0
        for i in range(1):
            for j in range(1):
                for k in range (96):
                    Y[k] = ticketsGiven[j][i][k]    
                    Yprob[k] = probabilities[j][i][k] * 100             
                plt.plot(X, Yprob, '-r')
                plt.bar(X, Y)
            plt.ylabel('probability')
            plt.xlabel('time interval')
            plt.savefig("day" + str(i) +".png")
        
