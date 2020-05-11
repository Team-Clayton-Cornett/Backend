from django.test import TestCase, Client
from rest_framework.test import APIClient
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
import json
import pickle
import datetime

from api.models import User, Park, Garage, Ticket

class ParkGetTestCase(TestCase):
    def setUp(self):
        # self.maxDiff = None
        self.client = APIClient()

        # import first (209 Hitt St) and second garage (AV1) from pickle dump
        with(open("api/tests/xgboost_tests_resources/garages.dat", "rb")) as file:
            garages = pickle.load(file)
            garage = garages[0]
            self.garage1 = Garage.objects.create(name=garage.name, start_enforce_time=garage.start_enforce_time, end_enforce_time=garage.end_enforce_time, enforced_on_weekends=garage.enforced_on_weekends, probability=garage.probability, latitude=garage.latitude, longitude=garage.longitude)
            garage = garages[1]
            self.garage2 = Garage.objects.create(name=garage.name, start_enforce_time=garage.start_enforce_time, end_enforce_time=garage.end_enforce_time, enforced_on_weekends=garage.enforced_on_weekends, probability=garage.probability, latitude=garage.latitude, longitude=garage.longitude)

        existing_user_data = {
            "email": "existing@user.com",
            "first_name": "Existing",
            "last_name": "User",
            "phone": "5735735733"
        }

        self.user1 = User.objects.create(**existing_user_data)
        self.user1.set_password("defaultpassword")
        self.user1.save()

        self.user1_token = Token.objects.create(user=self.user1)

        existing_user2_data = {
            "email": "existing2@user.com",
            "first_name": "Existing2",
            "last_name": "User",
            "phone": "3753753755"
        }

        self.user2 = User.objects.create(**existing_user2_data)
        self.user2.set_password("defaultpassword")
        self.user2.save()

        self.user2_token = Token.objects.create(user=self.user2)

        date_now = datetime.datetime.now()
        existing_park_data = {
            "start": date_now,
            "garage": self.garage1,
            "user_id": self.user1.pk
        }

        self.park1 = Park.objects.create(**existing_park_data)
        self.park1.save()

        existing_park_data['start'] -= datetime.timedelta(hours=2)
        existing_park_data['garage'] = self.garage2
        existing_park_data['end'] = existing_park_data['start'] + datetime.timedelta(hours=1)
        existing_park_data['ticket'] = Ticket(date=(existing_park_data['end'] - datetime.timedelta(minutes=30)))
        self.park2 = Park.objects.create(**existing_park_data)

    def test_park_get_valid(self):
        get_park_data = {}

        response = self.client.get('/api/user/park/', get_park_data, HTTP_AUTHORIZATION='Token ' + self.user1_token.key)
        response_content = json.loads(response.content)

        correct_response_content = [
            {
                'pk': self.park2.pk,
                'start': self.park2.start.replace(microsecond=((self.park2.start.microsecond // 1000) * 1000)).isoformat(),
                'end': self.park2.end.replace(microsecond=((self.park2.end.microsecond // 1000) * 1000)).isoformat(),
                'ticket': {
                    'date': self.park2.ticket.date.replace(microsecond=((self.park2.ticket.date.microsecond // 1000) * 1000)).isoformat(),
                    'day_of_week': self.park2.ticket.day_of_week()
                },
                'garage': {
                    'pk': self.garage2.pk,
                    'name': self.garage2.name
                },
                'user': self.user1.pk
            },
            {
                'pk': self.park1.pk,
                'start': self.park1.start.replace(microsecond=((self.park1.start.microsecond // 1000) * 1000)).isoformat(),
                'end': None,
                'ticket': None,
                'garage': {
                    'pk': self.garage1.pk,
                    'name': self.garage1.name
                },
                'user': self.user1.pk
            }
        ]

        # verify response is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content, correct_response_content)

    def test_park_get_valid_specific_park(self):
        get_park_data = {
            "pk": self.park2.pk
        }

        response = self.client.get('/api/user/park/', get_park_data, HTTP_AUTHORIZATION='Token ' + self.user1_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            'pk': self.park2.pk,
            'start': self.park2.start.replace(microsecond=((self.park2.start.microsecond // 1000) * 1000)).isoformat(),
            'end': self.park2.end.replace(microsecond=((self.park2.end.microsecond // 1000) * 1000)).isoformat(),
            'ticket': {
                'date': self.park2.ticket.date.replace(microsecond=((self.park2.ticket.date.microsecond // 1000) * 1000)).isoformat(),
                'day_of_week': self.park2.ticket.day_of_week()
            },
            'garage': {
                'pk': self.garage2.pk,
                'name': self.garage2.name
            },
            'user': self.user1.pk
        }

        # verify response is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content, correct_response_content)

    def test_park_get_valid_no_parks(self):
        get_park_data = {}

        response = self.client.get('/api/user/park/', get_park_data, HTTP_AUTHORIZATION='Token ' + self.user2_token.key)
        response_content = json.loads(response.content)

        correct_response_content = []

        # verify response is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content, correct_response_content)

    def test_park_get_invalid_specific_park_dne(self):
        get_park_data = {
            "pk": 99
        }

        response = self.client.get('/api/user/park/', get_park_data, HTTP_AUTHORIZATION='Token ' + self.user1_token.key)
        response_content = json.loads(response.content)

        correct_response_content = "The park with pk=99 does not exist."

        # verify response is correct
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_content, correct_response_content)

    def test_park_get_invalid_specific_park_belongs_to_other_user(self):
        get_park_data = {
            "pk": self.park1.pk
        }

        response = self.client.get('/api/user/park/', get_park_data, HTTP_AUTHORIZATION='Token ' + self.user2_token.key)
        response_content = json.loads(response.content)

        correct_response_content = "The user does not own the specified park."

        # verify response is correct
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_content, correct_response_content)

    def test_park_get_invalid_not_authenticated(self):
        get_park_data = {}

        response = self.client.get('/api/user/park/', get_park_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "detail": "Authentication credentials were not provided."
        }

        # verify response is correct
        self.assertEqual(response.status_code, 401, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")