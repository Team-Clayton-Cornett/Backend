import csv
import math
import json
import numpy as np
import os
import time
import pickle
import pandas as pd
import xgboost as xgb

from django.core.management.base import BaseCommand, CommandError
from xgboost import XGBClassifier
from datetime import date
from enum import IntEnum 
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import metrics
from sklearn.model_selection import GridSearchCV

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
# 0 1  * * * cd <project root> &&  nice -n 19 <project root>/venv/bin/python <project root>/manage.py xgboost_daily >> <cron output location> 2>&1

# old model params before auto-tuning:
#  model = XGBClassifier(
#             learning_rate = 0.1,
#             n_estimators = 1000,
#             scale_pos_weight=3,
#             max_depth = 5,
#             min_child_weight = 1,
#             gamma = 0.3,
#             subsample = 0.8,
#             colsample_bytree = 0.8,
#             objective = 'binary:logistic',
#             nthread = 4,
#             #scale_pos_weight = 1,
#             seed = 27
#         )

class Command(BaseCommand):
    help = '*Create Help Text*'

    def handle(self, *args, **options):
        # load today's training data
        self.create_csv()

        # load today's data
        today = date.today()
        dataset = np.loadtxt('training_data/tickets_' + today.strftime("%m-%d-%Y") +'.csv', delimiter=",", usecols=range(4), skiprows=1)

        # split data into X and y
        X = dataset[:,0:3]
        Y = dataset[:,3]

        # tune the xgboost parameters
        depth_weight = self.tune_depth_weight(X,Y)
        gamma = self.tune_gamma(X, Y)
        subsample_colsample = self.tune_subsample_colsample(X,Y)

        if(depth_weight == False or gamma == False or subsample_colsample == False):
            self.stdout.write('There was an error tuning model parameters')
            return

        # init model with new parameters
        model = XGBClassifier(
            learning_rate = 0.01,
            n_estimators = 3000,
            scale_pos_weight=3,
            max_depth = depth_weight[0],
            min_child_weight = depth_weight[1],
            gamma = gamma,
            subsample = subsample_colsample[0],
            colsample_bytree = subsample_colsample[1],
            objective = 'binary:logistic',
            nthread = 4,
            seed = 27
        )

        # fit model
        model.fit(X, Y)

        # evaluate model performance
        #self.modelfit(model, X, Y, useTrainCV=True, cv_folds=5, early_stopping_rounds=50)

        # save model params to file for loading later (TODO)
        today = date.today()
        filename = 'xgboost_models/' + today.strftime("%m-%d-%Y") + '.dat'
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'wb') as outfile:
            pickle.dump(model, outfile)

        # use updated model to write new probabilites for each time interval to the DB
        self.write_probabilities_to_database(model)

        self.stdout.write('The xgboost_daily task was ran at ' + str(today))

    # writes new probabilities to DB, based on the newly updated model
    def write_probabilities_to_database(self, model):
        if(model is None):
            return False

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
                    X_test[inx][2] = i + 1
                    inx = inx + 1

        try:
            # output is the probabilites for each time interval
            preds = model.predict_proba(X_test)
        except:
            return False

        i=0
        weekend = False
        # loop over all garages in DB and update with the new probabilites
        
        try:
            for garage in queryset:
                garage_probs_new = []
                for garage_day_prob in garage.probability:
                    if garage_day_prob.day_of_week == DAYS_OF_WEEK[0][0] or garage_day_prob.day_of_week == DAYS_OF_WEEK[6][0]:
                        weekend = True
                    else:
                        weekend = False

                    day_probs_new = []
                    j=0
                    for garage_interval_prob in garage_day_prob.probability:
                        # time < 7:00am or time > 6:00pm
                        if j < 28 or j > 72 or weekend == True:
                            garage_interval_prob.probability = 0.01
                        else:
                            garage_interval_prob.probability = preds[i][1]
                        i=i+1
                        j=j+1

                        day_probs_new.append(garage_interval_prob)
                    garage_day_prob.probability = day_probs_new
                    garage_probs_new.append(garage_day_prob)
                # overwrite old probabiliy list
                garage.probability = garage_probs_new
                
                if garage and garage_probs_new:
                    garage.save()
        except:
            return False

        return True

    # outputs probs to a file
    def output_probs(self, model, filepath="training_data/pred.txt"):
        X_test = np.zeros((51744,3))
        inx = 0
        for i in range(77):
            for j in range(7):
                for k in range(96):
                    X_test[inx][0] = k
                    X_test[inx][1] = j
                    X_test[inx][2] = i
                    inx = inx + 1

        try:
            preds = model.predict_proba(X_test)
            
            with open(filepath, "w") as file:
                np.savetxt(file, preds)
        except:
            return False
        
        return True
                      


    # Creates /opt/capstone/training_data/tickets<date>.csv with relevent training data from current DB state
    def create_csv(self, filename=('training_data/tickets_'+date.today().strftime("%m-%d-%Y") +'.csv')):
        training_set = None
        writer = None
        try:
            # just in case training_data dir does not exist yet
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            training_set = open((filename), 'w', newline='')
        except:
            return False

        try:
            # the data we are training on
            writer = csv.writer(training_set)
            writer.writerow(['time','day_of_week', 'garage', 'ticketed'])
        except:
            return False

        # gets all parks that do have a ticket
        parksTicketed = Park.objects.exclude(ticket = None).exclude(end = None).iterator()
        ticketCount = Park.objects.exclude(ticket = None).exclude(end = None).count()

        if(parksTicketed is not None):
            write_queue = []

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
                dayCode = ((dateTimeTicketed.weekday() + 1) % 7)

                # ticket the time interval of ticketing, otherwise create a non ticket event
                for i in range(startOffset, endOffset + 1):
                    if(i == ticketOffset): 
                        write_queue.append((i, dayCode, garage, int(WasTicketed.YES)))
                    else:
                        write_queue.append((i, dayCode, garage, int(WasTicketed.NO)))

                if len(write_queue) > 100 or ticketCount < 100:
                    writer.writerows(write_queue)  
                    write_queue.clear()
                    time.sleep(0.01)

        # gets all parks that did not result in a ticket
        parksNotTicketed = Park.objects.filter(ticket = None).exclude(end = None).iterator()
        ticketCount = Park.objects.filter(ticket = None).exclude(end = None).count()
        if(parksNotTicketed is not None):
            write_queue = []

            for park in parksNotTicketed:
                startTime = park.start
                endTime = park.end
                # the int representation of a garage
                garage = park.garage.id

                # gets 15 minute time interval offset
                startOffset = math.floor(((startTime.hour * 60) + startTime.minute)/15)
                endOffset = math.floor(((endTime.hour * 60) + endTime.minute)/15)

                # the int representation of a weekday
                dayCode = ((startTime.weekday() + 1) % 7)

                # there will always be not ticket events
                for i in range(startOffset, endOffset + 1):
                    write_queue.append((i, dayCode, garage, int(WasTicketed.NO)))
                
                if len(write_queue) > 100 or ticketCount < 100:
                    writer.writerows(write_queue)  
                    write_queue.clear()
                    time.sleep(0.01)

        training_set.close()

        return True

    # evaluates model accuracy
    def modelfit(self, alg, X, Y, useTrainCV=True, cv_folds=5, early_stopping_rounds=50):
        try:
            if useTrainCV:
                xgb_param = alg.get_xgb_params()
                xgtrain = xgb.DMatrix(X, label=Y)
                cvresult = xgb.cv(xgb_param, xgtrain, num_boost_round=alg.get_params()['n_estimators'], nfold=cv_folds,
                    metrics='auc', early_stopping_rounds=early_stopping_rounds, verbose_eval=False)
                alg.set_params(n_estimators=cvresult.shape[0])
            else:
                return False
        except:
            return False
        
        try:
            #Fit the algorithm on the data
            alg.fit(X, Y, eval_metric='auc')
                
            #Predict training set:
            dtrain_predictions = alg.predict(X)
            dtrain_predprob = alg.predict_proba(X)[:,1]
        except:
            return False
            
        #Print model report:
        self.stdout.write("\nModel Report")
        self.stdout.write("Accuracy : %.4g" % metrics.accuracy_score(Y, dtrain_predictions))
        self.stdout.write("AUC Score (Train): %f" % metrics.roc_auc_score(Y, dtrain_predprob))

        return True

    # tunes max_depth and min_child_weight parameters
    def tune_depth_weight(self, X, Y):
        
        if(X is None or Y is None):
            return False
         
        param_test1 = {
            'max_depth':range(3,10,2),
            'min_child_weight':range(1,6,2)
        }

        try:
            gsearch1 = GridSearchCV(estimator = XGBClassifier( learning_rate=0.1, n_estimators=140, max_depth=5,
            min_child_weight=2, gamma=0, subsample=0.8, colsample_bytree=0.8,
            objective= 'binary:logistic', nthread=4, scale_pos_weight=3,seed=27), 
            param_grid = param_test1, scoring='roc_auc',n_jobs=4, cv=5)
            gsearch1.fit(X,Y)
        except:
            return False

        try:
            n1 = gsearch1.best_params_['max_depth']
            n2 = gsearch1.best_params_['min_child_weight']
        except:
            return False
        
        param_test2 = {
            'max_depth':[n1-1,n1,n1+1],
            'min_child_weight':[n2-1,n2,n2+1]
        }

        try:
            gsearch2 = GridSearchCV(estimator = XGBClassifier( learning_rate=0.1, n_estimators=140, max_depth=5,
            min_child_weight=2, gamma=0, subsample=0.8, colsample_bytree=0.8,
            objective= 'binary:logistic', nthread=4, scale_pos_weight=3,seed=27), 
            param_grid = param_test2, scoring='roc_auc',n_jobs=4, cv=5)
            gsearch2.fit(X,Y)
        except:
            return False

        return (gsearch2.best_params_['max_depth'], gsearch2.best_params_['min_child_weight'])
    
    # tunes gamma parameter
    def tune_gamma(self, X, Y):
        param_test3 = {
            'gamma':[i/10.0 for i in range(0,5)]
        }

        try:
            gsearch3 = GridSearchCV(estimator = XGBClassifier( learning_rate =0.1, n_estimators=140, max_depth=10,
            min_child_weight=0, gamma=0, subsample=0.8, colsample_bytree=0.8,
            objective= 'binary:logistic', nthread=4, scale_pos_weight=3,seed=27), 
            param_grid = param_test3, scoring='roc_auc',n_jobs=4, cv=5)
            gsearch3.fit(X,Y)
        except:
            return False

        return gsearch3.best_params_['gamma']
    
    # tunes subsample and colsample_bytree parameters
    def tune_subsample_colsample(self, X, Y):
        param_test4 = {
            'subsample':[i/10.0 for i in range(6,10)],
            'colsample_bytree':[i/10.0 for i in range(6,10)]
        }
        try:
            gsearch4 = GridSearchCV(estimator = XGBClassifier( learning_rate =0.1, n_estimators=177, max_depth=10,
            min_child_weight=0, gamma=0.1, subsample=0.8, colsample_bytree=0.8,
            objective= 'binary:logistic', nthread=4, scale_pos_weight=1,seed=27), 
            param_grid = param_test4, scoring='roc_auc',n_jobs=4, cv=5)
            gsearch4.fit(X,Y)
        except:
            return False

        return (gsearch4.best_params_['subsample'], gsearch4.best_params_['colsample_bytree'])
                