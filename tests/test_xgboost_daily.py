from django.test import TestCase
from api.management.commands.xgboost_daily import *
from unittest.mock import MagicMock

import api.management.commands
import datetime as datetime
import unittest.mock as mock
import builtins

class XGBoostDailyTestCase(TestCase):        
    def setUp(self):
        with(open("tests/garages.dat", "rb")) as file:
            garages = pickle.load(file)
            for garage in garages:
                Garage.objects.create(name=garage.name, start_enforce_time=garage.start_enforce_time, end_enforce_time=garage.end_enforce_time, enforced_on_weekends=garage.enforced_on_weekends, probability=garage.probability, latitude=garage.latitude, longitude=garage.longitude)

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

    def test_output_probs_good_model(self):
        
        fake_file_path = "tests/file"

        with mock.patch('api.management.commands.xgboost_daily.open', mock.mock_open()) as mocked_file:
            alg = pickle.load(open("tests/mock_model/03-30-2020.dat", "rb"))
            assert alg is not None

            command = Command()
            res = command.output_probs(alg, fake_file_path)

            assert res is True
            mocked_file.assert_called_once_with(fake_file_path, 'w')
            self.assertEqual(mocked_file().write.call_count, 51744)
    
    def test_output_probs_bad_model(self):
        
        fake_file_path = "tests/file"

        with mock.patch('api.management.commands.xgboost_daily.open', mock.mock_open()) as mocked_file:
            alg = None

            command = Command()
            res = command.output_probs(alg, fake_file_path)

            assert res is False
            self.assertEqual(mocked_file.call_count, 0)
            self.assertEqual(mocked_file().write.call_count, 0)

    def test_output_probs_bad_file_write(self):
        
        fake_file_path = "tests/file"

        with mock.patch('api.management.commands.xgboost_daily.open', mock.mock_open()) as mocked_file:
            alg = pickle.load(open("tests/mock_model/03-30-2020.dat", "rb"))
            assert alg is not None

            mocked_file.side_effect = Exception("test exception")

            command = Command()
            res = command.output_probs(alg, fake_file_path)

            assert res is False
            self.assertEqual(mocked_file.call_count, 1)
    
    def test_write_probabilities_to_database_good_params(self):
        alg = None

        command = Command()
        res = command.write_probabilities_to_database(alg)

        assert res is False

    def test_write_probabilities_to_database_bad_model(self):
        alg = pickle.load(open("tests/mock_model/03-30-2020.dat", "rb"))
        assert alg is not None

        command = Command()
        res = command.write_probabilities_to_database(alg)
        self.assertEqual(Garage.objects.all().count(), 77)

        garages = Garage.objects.all()

        for i in range(77):
            for j in range(7):
                for k in range(96):
                    self.assertGreater(garages[i].probability[j].probability[k].probability, 0)

        assert res is True

    # def test_create_csv_good_params(self):

    #     start_date = datetime.datetime(2020,1,1,11,0,0)
    #     end_date = datetime.datetime(2020,1,1,13,0,0)
    #     ticket_date = datetime.datetime(2020,1,1,12,0,0)
        
    #     with(open("tests/garages.dat", "rb")) as file:
    #         garages = pickle.load(file)
    #         for garage in garages:
    #             Garage.objects.create(name=garage.name, start_enforce_time=garage.start_enforce_time, end_enforce_time=garage.end_enforce_time, enforced_on_weekends=garage.enforced_on_weekends, probability=garage.probability, latitude=garage.latitude, longitude=garage.longitude)            