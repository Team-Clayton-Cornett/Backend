from django.test import TestCase
from api.management.commands.xgboost_daily import *

import api.management.commands

import unittest.mock as mock
from unittest.mock import MagicMock

class XGBoostDailyTestCase(TestCase):
    def test_tune_depth_weight_good_params(self):

        l1 = [[1,1],[2,2],[3,3],[4,4],[5,5],[6,6],[7,7],[8,8],[9,9],[10,10]]
        l2 = [1,1,1,1,1,0,0,0,0,0]

        X = np.array(l1)
        Y = np.array(l2)

        command = Command()
        res = command.tune_depth_weight(X, Y)

        assert res is not None

    def test_tune_depth_weight_bad_params(self):
        X = None
        Y = None

        command = Command()
        res = command.tune_depth_weight(X, Y)

        assert res is False
    
    @mock.patch("api.management.commands.xgboost_daily.GridSearchCV")
    def test_tune_depth_weight_bad_grid_search_res(self, mock_gridsearch):
        l1 = [[1,1],[2,2],[3,3],[4,4],[5,5],[6,6],[7,7],[8,8],[9,9],[10,10]]
        l2 = [1,1,1,1,1,0,0,0,0,0]        

        mock_gridsearch.return_value = None

        X = np.array(l1)
        Y = np.array(l2)

        command = Command()
        res = command.tune_gamma(X, Y)

        assert res is False
    
    def test_tune_gamma_good_params(self):

        l1 = [[1,1],[2,2],[3,3],[4,4],[5,5],[6,6],[7,7],[8,8],[9,9],[10,10]]
        l2 = [1,1,1,1,1,0,0,0,0,0]

        X = np.array(l1)
        Y = np.array(l2)

        command = Command()
        res = command.tune_gamma(X, Y)

        assert res is not None

    def test_tune_gamma_bad_params(self):
        X = None
        Y = None

        command = Command()
        res = command.tune_gamma(X, Y)

        assert res is False
    
    @mock.patch("api.management.commands.xgboost_daily.GridSearchCV")
    def test_tune_gamma_bad_grid_search_res(self, mock_gridsearch):
        l1 = [[1,1],[2,2],[3,3],[4,4],[5,5],[6,6],[7,7],[8,8],[9,9],[10,10]]
        l2 = [1,1,1,1,1,0,0,0,0,0]        

        mock_gridsearch.return_value = None

        X = np.array(l1)
        Y = np.array(l2)

        command = Command()
        res = command.tune_gamma(X, Y)

        assert res is False

    def test_tune_subsample_colsample_good_params(self):

        l1 = [[1,1],[2,2],[3,3],[4,4],[5,5],[6,6],[7,7],[8,8],[9,9],[10,10]]
        l2 = [1,1,1,1,1,0,0,0,0,0]

        X = np.array(l1)
        Y = np.array(l2)

        command = Command()
        res = command.tune_subsample_colsample(X, Y)

        assert res is not None

    def test_tune_subsample_colsample_bad_params(self):
        X = None
        Y = None

        command = Command()
        res = command.tune_subsample_colsample(X, Y)

        assert res is False
    
    @mock.patch("api.management.commands.xgboost_daily.GridSearchCV")
    def test_tune_subsample_colsample_bad_grid_search_res(self, mock_gridsearch):
        l1 = [[1,1],[2,2],[3,3],[4,4],[5,5],[6,6],[7,7],[8,8],[9,9],[10,10]]
        l2 = [1,1,1,1,1,0,0,0,0,0]        

        mock_gridsearch.return_value = None

        X = np.array(l1)
        Y = np.array(l2)

        command = Command()
        res = command.tune_subsample_colsample(X, Y)

        assert res is False

    def test_model_fit_good_params(self):
        alg = pickle.load(open("tests/mock_model/03-30-2020.dat", "rb"))

        assert alg is not None

        l1 = [[1,1],[2,2],[3,3],[4,4],[5,5],[6,6],[7,7],[8,8],[9,9],[10,10]]
        l2 = [1,1,1,1,1,0,0,0,0,0]        

        X = np.array(l1)
        Y = np.array(l2)

        command = Command()
        res = command.modelfit(alg, X, Y)

        assert res is True
    
    def test_model_fit_bad_params(self):
        alg = None 
        X = None
        Y = None

        command = Command()
        res = command.modelfit(alg, X, Y)

        assert res is False


