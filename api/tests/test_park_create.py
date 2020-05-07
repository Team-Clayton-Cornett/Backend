from django.test import TestCase
from rest_framework.test import APIClient
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
import json
import pickle
import datetime

from api.models import User, Park, Garage

class ParkCreateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # import first garage (209 Hitt St) from pickle dump
        with(open("api/tests/xgboost_tests_resources/garages.dat", "rb")) as file:
            garages = pickle.load(file)
            garage = garages[0]
            self.garage = Garage.objects.create(name=garage.name, start_enforce_time=garage.start_enforce_time, end_enforce_time=garage.end_enforce_time, enforced_on_weekends=garage.enforced_on_weekends, probability=garage.probability, latitude=garage.latitude, longitude=garage.longitude)

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

    def test_park_create_valid(self):
        date_now = datetime.datetime.now()

        create_park_data = {
            "start": date_now.isoformat(),
            "garage_id": self.garage.pk
        }

        response = self.client.post('/api/user/park/', create_park_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "pk": 1,
            "start": date_now.isoformat(),
            "end": None,
            "ticket": None,
            "garage": {
                "pk": self.garage.pk,
                "name": "209 Hitt St"
            },
            "user": self.user.pk
        }

        # verify response is correct
        self.assertEqual(response.status_code, 201, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify park was created
        user_parks = self.user.parks()
        self.assertTrue(len(user_parks) > 0, msg="Park instance was not created in database.")

        # verify park has correct data
        created_park = user_parks[0]
        created_park_data = model_to_dict(created_park, fields=['start', 'end', 'ticket', 'garage', 'user'])
        trimmed_date_now = date_now.replace(microsecond=((date_now.microsecond // 1000) * 1000))

        correct_park_data = {
            "start": trimmed_date_now,
            "end": None,
            "ticket": None,
            "garage": self.garage.pk,
            "user": self.user.pk
        }

        self.assertEqual(created_park_data, correct_park_data, msg="Park instance data was incorrect.")

    def test_park_create_invalid_garage(self):
        date_now = datetime.datetime.now()

        create_park_data = {
            "start": date_now.isoformat(),
            "garage_id": 99
        }

        response = self.client.post('/api/user/park/', create_park_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            'garage_id': [
                'Invalid pk "99" - object does not exist.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_park_create_invalid_no_garage(self):
        date_now = datetime.datetime.now()

        create_park_data = {
            "start": date_now.isoformat()
        }

        response = self.client.post('/api/user/park/', create_park_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            'garage_id': [
                'This field is required.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")


    def test_park_create_invalid_start(self):
        create_park_data = {
            "start": '',
            "garage_id": self.garage.pk
        }

        response = self.client.post('/api/user/park/', create_park_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            'start': [
                'Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_park_create_invalid_no_start(self):
        create_park_data = {
            "garage_id": self.garage.pk
        }

        response = self.client.post('/api/user/park/', create_park_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            'start': [
                'This field is required.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_park_create_invalid(self):
        create_park_data = {
            "start": '',
            "garage_id": 99
        }

        response = self.client.post('/api/user/park/', create_park_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            'garage_id': [
                'Invalid pk "99" - object does not exist.'
            ],
            'start': [
                'Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_park_create_not_authenticated(self):
        date_now = datetime.datetime.now()

        create_park_data = {
            "start": date_now,
            "garage_id": self.garage.pk
        }

        response = self.client.post('/api/user/park/', create_park_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "detail": "Authentication credentials were not provided."
        }

        # verify response is correct
        self.assertEqual(response.status_code, 401, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")