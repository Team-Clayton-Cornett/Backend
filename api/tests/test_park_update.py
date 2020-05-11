from django.test import TestCase
from rest_framework.test import APIClient
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
import json
import pickle
import datetime
import dateutil.parser

from api.models import User, Park, Garage
from api.serializers import ParkSerializer

class ParkUpdateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # import first garage (209 Hitt St) from pickle dump
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

        self.user = User.objects.create(**existing_user_data)
        self.user.set_password("defaultpassword")
        self.user.save()

        self.user_token = Token.objects.create(user=self.user)

        date_now = datetime.datetime.now()
        existing_park_data = {
            "start": date_now,
            "garage": self.garage1,
            "user_id": self.user.pk
        }

        self.park = Park.objects.create(**existing_park_data)
        self.park.save()

    def test_park_update_valid(self):
        existing_park_data = ParkSerializer(self.park).data
        date_now = datetime.datetime.now()

        update_park_data = {
            "pk": self.park.pk,
            "end": date_now.isoformat(),
            "garage_id": self.garage2.pk
        }

        response = self.client.patch('/api/user/park/', update_park_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        park_start_date = dateutil.parser.isoparse(existing_park_data['start'])
        trimmed_park_start = park_start_date.replace(microsecond=((park_start_date.microsecond // 1000) * 1000))

        correct_response_content = existing_park_data.copy()
        correct_response_content['start'] = trimmed_park_start.isoformat()
        correct_response_content['end'] = date_now.isoformat()
        correct_response_content['garage'] = {
            "pk": self.garage2.pk,
            "name": self.garage2.name
        }

        # verify response is correct
        self.assertEqual(response.status_code, 200, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify park has correct data
        updated_park = Park.objects.get(pk=self.park.pk)
        updated_park_data = model_to_dict(updated_park, fields=['start', 'end', 'ticket', 'garage', 'user'])
        trimmed_date_now = date_now.replace(microsecond=((date_now.microsecond // 1000) * 1000))

        correct_park_data = {
            "start": trimmed_park_start,
            "end": trimmed_date_now,
            "ticket": existing_park_data['ticket'],
            "garage": self.garage2.pk,
            "user": existing_park_data['user']
        }

        self.assertEqual(updated_park_data, correct_park_data, msg="Park instance data was incorrect.")

    def test_park_update_valid_end(self):
        existing_park_data = ParkSerializer(self.park).data
        date_now = datetime.datetime.now()

        update_park_data = {
            "pk": self.park.pk,
            "end": date_now.isoformat()
        }

        response = self.client.patch('/api/user/park/', update_park_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        park_start_date = dateutil.parser.isoparse(existing_park_data['start'])
        trimmed_park_start = park_start_date.replace(microsecond=((park_start_date.microsecond // 1000) * 1000))

        correct_response_content = existing_park_data.copy()
        correct_response_content['start'] = trimmed_park_start.isoformat()
        correct_response_content['end'] = date_now.isoformat()

        # verify response is correct
        self.assertEqual(response.status_code, 200, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify park has correct data
        updated_park = Park.objects.get(pk=self.park.pk)
        updated_park_data = model_to_dict(updated_park, fields=['start', 'end', 'ticket', 'garage', 'user'])
        trimmed_date_now = date_now.replace(microsecond=((date_now.microsecond // 1000) * 1000))

        correct_park_data = {
            "start": trimmed_park_start,
            "end": trimmed_date_now,
            "ticket": existing_park_data['ticket'],
            "garage": existing_park_data['garage']['pk'],
            "user": existing_park_data['user']
        }

        self.assertEqual(updated_park_data, correct_park_data, msg="Park instance data was incorrect.")

    def test_park_update_valid_garage(self):
        existing_park_data = ParkSerializer(self.park).data
        date_now = datetime.datetime.now()

        update_park_data = {
            "pk": self.park.pk,
            "garage_id": self.garage2.pk
        }

        response = self.client.patch('/api/user/park/', update_park_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        park_start_date = dateutil.parser.isoparse(existing_park_data['start'])
        trimmed_park_start = park_start_date.replace(microsecond=((park_start_date.microsecond // 1000) * 1000))

        correct_response_content = existing_park_data.copy()
        correct_response_content['start'] = trimmed_park_start.isoformat()
        correct_response_content['garage'] = {
            "pk": self.garage2.pk,
            "name": self.garage2.name
        }

        # verify response is correct
        self.assertEqual(response.status_code, 200, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify park has correct data
        updated_park = Park.objects.get(pk=self.park.pk)
        updated_park_data = model_to_dict(updated_park, fields=['start', 'end', 'ticket', 'garage', 'user'])
        trimmed_date_now = date_now.replace(microsecond=((date_now.microsecond // 1000) * 1000))

        correct_park_data = {
            "start": trimmed_park_start,
            "end": existing_park_data['end'],
            "ticket": existing_park_data['ticket'],
            "garage": self.garage2.pk,
            "user": existing_park_data['user']
        }

        self.assertEqual(updated_park_data, correct_park_data, msg="Park instance data was incorrect.")

    def test_park_update_invalid_start(self):
        update_park_data = {
            "pk": self.park.pk,
            "start": ''
        }

        response = self.client.patch('/api/user/park/', update_park_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            'start': [
                'Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_park_update_invalid_garage(self):
        date_now = datetime.datetime.now()

        update_park_data = {
            "pk": self.park.pk,
            "garage_id": 99
        }

        response = self.client.patch('/api/user/park/', update_park_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            'garage_id': [
                'Invalid pk "99" - object does not exist.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_park_update_invalid_no_pk(self):
        date_now = datetime.datetime.now()

        update_park_data = {
            "garage_id": self.garage2.pk
        }

        response = self.client.patch('/api/user/park/', update_park_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            'pk': [
                'This field is required.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_park_update_invalid(self):
        update_park_data = {
            "pk": self.park.pk,
            "start": '',
            "garage_id": 99
        }

        response = self.client.patch('/api/user/park/', update_park_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
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

    def test_park_update_not_authenticated(self):
        date_now = datetime.datetime.now()

        update_park_data = {
            "pk": self.park.pk,
            "start": date_now.isoformat(),
            "garage_id": self.garage2.pk
        }

        response = self.client.patch('/api/user/park/', update_park_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "detail": "Authentication credentials were not provided."
        }

        # verify response is correct
        self.assertEqual(response.status_code, 401, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")