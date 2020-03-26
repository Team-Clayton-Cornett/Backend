import csv
import math
import json
import numpy as np
import os

from django.core.management.base import BaseCommand, CommandError
from xgboost import XGBClassifier
from datetime import date
from enum import IntEnum 
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


import pandas as pd
import xgboost as xgb
from sklearn import metrics   #Additional scklearn functions
from sklearn.model_selection import GridSearchCV   #Perforing grid search

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

    def modelfit(self, alg, X, Y, useTrainCV=True, cv_folds=5, early_stopping_rounds=50):
        if useTrainCV:
            xgb_param = alg.get_xgb_params()
            xgtrain = xgb.DMatrix(X, label=Y)
            cvresult = xgb.cv(xgb_param, xgtrain, num_boost_round=alg.get_params()['n_estimators'], nfold=cv_folds,
                metrics='auc', early_stopping_rounds=early_stopping_rounds, verbose_eval=False)
            alg.set_params(n_estimators=cvresult.shape[0])
        
        #Fit the algorithm on the data
        alg.fit(X, Y, eval_metric='auc')
            
        #Predict training set:
        dtrain_predictions = alg.predict(X)
        dtrain_predprob = alg.predict_proba(X)[:,1]
            
        #Print model report:
        print("\nModel Report")
        print("Accuracy : %.4g" % metrics.accuracy_score(Y, dtrain_predictions))
        print("AUC Score (Train): %f" % metrics.roc_auc_score(Y, dtrain_predprob))

    def tune_depth_weight(self, X, Y):
        param_test1 = {
            'max_depth':range(3,10,2),
            'min_child_weight':range(1,6,2)
        }

        gsearch1 = GridSearchCV(estimator = XGBClassifier( learning_rate=0.1, n_estimators=140, max_depth=5,
        min_child_weight=2, gamma=0, subsample=0.8, colsample_bytree=0.8,
        objective= 'binary:logistic', nthread=4, scale_pos_weight=1,seed=27), 
        param_grid = param_test1, scoring='roc_auc',n_jobs=4, cv=5)
        gsearch1.fit(X,Y)
        for i in ['mean_test_score', 'std_test_score', 'params']:
            print(i," : ", gsearch1.cv_results_[i])

        n1 = gsearch1.best_params_['max_depth']
        n2 = gsearch1.best_params_['min_child_weight']
        
        param_test2 = {
            'max_depth':[n1-1,n1,n1+1],
            'min_child_weight':[n2-1,n2,n2+1]
        }

        gsearch2 = GridSearchCV(estimator = XGBClassifier( learning_rate=0.1, n_estimators=140, max_depth=5,
        min_child_weight=2, gamma=0, subsample=0.8, colsample_bytree=0.8,
        objective= 'binary:logistic', nthread=4, scale_pos_weight=1,seed=27), 
        param_grid = param_test2, scoring='roc_auc',n_jobs=4, cv=5)
        gsearch2.fit(X,Y)
        for i in ['mean_test_score', 'std_test_score', 'params']:
            print(i," : ", gsearch2.cv_results_[i])

        print(gsearch2.best_params_, gsearch2.best_score_)
    def tune_gamma(self, X, Y):
        param_test3 = {
            'gamma':[i/10.0 for i in range(0,5)]
        }
        gsearch3 = GridSearchCV(estimator = XGBClassifier( learning_rate =0.1, n_estimators=140, max_depth=10,
        min_child_weight=0, gamma=0, subsample=0.8, colsample_bytree=0.8,
        objective= 'binary:logistic', nthread=4, scale_pos_weight=1,seed=27), 
        param_grid = param_test3, scoring='roc_auc',n_jobs=4, cv=5)
        gsearch3.fit(X,Y)
        for i in ['mean_test_score', 'std_test_score', 'params']:
            print(i," : ", gsearch3.cv_results_[i])
        print(gsearch3.best_params_, gsearch3.best_score_)
    def tune_subsample_colsample(self, X, Y):
        param_test4 = {
            'subsample':[i/10.0 for i in range(6,10)],
            'colsample_bytree':[i/10.0 for i in range(6,10)]
        }
        gsearch4 = GridSearchCV(estimator = XGBClassifier( learning_rate =0.1, n_estimators=177, max_depth=10,
        min_child_weight=0, gamma=0.1, subsample=0.8, colsample_bytree=0.8,
        objective= 'binary:logistic', nthread=4, scale_pos_weight=1,seed=27), 
        param_grid = param_test4, scoring='roc_auc',n_jobs=4, cv=5)
        gsearch4.fit(X,Y)
        for i in ['mean_test_score', 'std_test_score', 'params']:
            print(i," : ", gsearch4.cv_results_[i])
        print(gsearch4.best_params_, gsearch4.best_score_)

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
        model = XGBClassifier(
            learning_rate =0.01,
            n_estimators=5000,
            max_depth=10,
            min_child_weight=0,
            gamma=0.1,
            subsample=0.6,
            colsample_bytree=0.7,
            objective= 'binary:logistic',
            nthread=4,
            scale_pos_weight=1,
            seed=27
        )

        model.fit(X, Y)

        #self.modelfit( model, X, Y)

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
                