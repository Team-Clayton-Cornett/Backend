from django.test import TestCase, Client
from rest_framework.test import APIClient
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
import json
import pickle
import datetime

from api.models import Garage, User
from api.serializers import GarageSerializer

class GarageGetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        existing_user_data = {
            "email": "existing@user.com",
            "first_name": "Existing",
            "last_name": "User",
            "phone": "5735735733"
        }

        self.user = User.objects.create(**existing_user_data)
        self.user.set_password("defaultpassword")
        self.user.save()

        self.user_token = Token.objects.create(user=self.user)

    def test_garage_get_valid(self):
        # import first (209 Hitt St) and second garage (AV1) from pickle dump
        with(open("api/tests/xgboost_tests_resources/garages.dat", "rb")) as file:
            garages = pickle.load(file)
            garage = garages[0]
            self.garage1 = Garage.objects.create(name=garage.name, start_enforce_time=garage.start_enforce_time, end_enforce_time=garage.end_enforce_time, enforced_on_weekends=garage.enforced_on_weekends, probability=garage.probability, latitude=garage.latitude, longitude=garage.longitude)
            garage = garages[1]
            self.garage2 = Garage.objects.create(name=garage.name, start_enforce_time=garage.start_enforce_time, end_enforce_time=garage.end_enforce_time, enforced_on_weekends=garage.enforced_on_weekends, probability=garage.probability, latitude=garage.latitude, longitude=garage.longitude)

        response = self.client.get('/api/garage/' + str(self.garage1.pk) + '/', HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        serializer = GarageSerializer(self.garage1)
        correct_response_content = serializer.data

        # verify response is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content, correct_response_content)

    def test_garage_get_invalid_garage_dne(self):
        # import first (209 Hitt St) and second garage (AV1) from pickle dump
        with(open("api/tests/xgboost_tests_resources/garages.dat", "rb")) as file:
            garages = pickle.load(file)
            garage = garages[0]
            self.garage1 = Garage.objects.create(name=garage.name, start_enforce_time=garage.start_enforce_time, end_enforce_time=garage.end_enforce_time, enforced_on_weekends=garage.enforced_on_weekends, probability=garage.probability, latitude=garage.latitude, longitude=garage.longitude)
            garage = garages[1]
            self.garage2 = Garage.objects.create(name=garage.name, start_enforce_time=garage.start_enforce_time, end_enforce_time=garage.end_enforce_time, enforced_on_weekends=garage.enforced_on_weekends, probability=garage.probability, latitude=garage.latitude, longitude=garage.longitude)

        response = self.client.get('/api/garage/99/', HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "detail": "Not found."
        }

        # verify response is correct
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_content, correct_response_content)

    def test_garage_get_invalid_not_authenticated(self):
        # import first (209 Hitt St) and second garage (AV1) from pickle dump
        with(open("api/tests/xgboost_tests_resources/garages.dat", "rb")) as file:
            garages = pickle.load(file)
            garage = garages[0]
            self.garage1 = Garage.objects.create(name=garage.name, start_enforce_time=garage.start_enforce_time, end_enforce_time=garage.end_enforce_time, enforced_on_weekends=garage.enforced_on_weekends, probability=garage.probability, latitude=garage.latitude, longitude=garage.longitude)
            garage = garages[1]
            self.garage2 = Garage.objects.create(name=garage.name, start_enforce_time=garage.start_enforce_time, end_enforce_time=garage.end_enforce_time, enforced_on_weekends=garage.enforced_on_weekends, probability=garage.probability, latitude=garage.latitude, longitude=garage.longitude)

        response = self.client.get('/api/garage/' + str(self.garage1.pk) + '/')
        response_content = json.loads(response.content)

        correct_response_content = {
            "detail": "Authentication credentials were not provided."
        }

        # verify response is correct
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_content, correct_response_content)