from django.test import TestCase
from rest_framework.test import APIClient
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
import json
import pickle
import datetime
import dateutil.parser

from api.models import User, Park, Garage, Ticket
from api.serializers import ParkSerializer

class ParkUpdateTestCase(TestCase):
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

        date_now = datetime.datetime.now()
        existing_park_data = {
            "start": date_now,
            "end": date_now + datetime.timedelta(hours=2),
            "ticket": Ticket(date=date_now + datetime.timedelta(hours=1)),
            "garage": self.garage,
            "user_id": self.user.pk
        }

        self.park = Park.objects.create(**existing_park_data)
        self.park.save()

    def test_ticket_update_valid(self):
        existing_park_data = ParkSerializer(self.park).data

        park_start_date = dateutil.parser.isoparse(existing_park_data['start'])
        trimmed_park_start = park_start_date.replace(microsecond=((park_start_date.microsecond // 1000) * 1000))

        park_end_date = dateutil.parser.isoparse(existing_park_data['end'])
        trimmed_park_end = park_end_date.replace(microsecond=((park_end_date.microsecond // 1000) * 1000))

        ticket_date = park_start_date + datetime.timedelta(minutes=30)
        trimmed_ticket_date = ticket_date.replace(microsecond=((ticket_date.microsecond // 1000) * 1000))

        update_ticket_data = {
            "park_id": self.park.pk,
            "date": ticket_date.isoformat()
        }

        response = self.client.patch('/api/user/ticket/', update_ticket_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "date": ticket_date.isoformat()
        }

        # verify response is correct
        self.assertEqual(response.status_code, 201, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify park has correct data
        updated_park = Park.objects.get(pk=self.park.pk)
        updated_park_data = model_to_dict(updated_park, fields=['start', 'end', 'garage', 'user'])

        correct_park_data = {
            "start": trimmed_park_start,
            "end": trimmed_park_end,
            "garage": existing_park_data['garage']['pk'],
            "user": existing_park_data['user']
        }

        self.assertEqual(updated_park_data, correct_park_data, msg="Park instance data was incorrect.")
        self.assertEqual(updated_park.ticket.date, trimmed_ticket_date, msg="Park instance ticket data was incorrect")

    def test_ticket_update_invalid_date(self):
        update_ticket_data = {
            "park_id": self.park.pk,
            "date": ''
        }

        response = self.client.patch('/api/user/ticket/', update_ticket_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            'date': [
                'Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_ticket_update_invalid_date_outside_park(self):
        existing_park_data = ParkSerializer(self.park).data

        park_start_date = dateutil.parser.isoparse(existing_park_data['start'])
        trimmed_park_start = park_start_date.replace(microsecond=((park_start_date.microsecond // 1000) * 1000))

        park_end_date = dateutil.parser.isoparse(existing_park_data['end'])
        trimmed_park_end = park_end_date.replace(microsecond=((park_end_date.microsecond // 1000) * 1000))

        ticket_date = park_start_date - datetime.timedelta(hours=1)

        # date before start
        update_ticket_data = {
            "park_id": self.park.pk,
            "date": ticket_date.isoformat()
        }

        response = self.client.patch('/api/user/ticket/', update_ticket_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            'date': [
                'The date of the ticket must be during park time.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        ticket_date = park_end_date + datetime.timedelta(hours=1)

        # date after end
        update_ticket_data = {
            "park_id": self.park.pk,
            "date": ticket_date.isoformat()
        }

        response = self.client.patch('/api/user/ticket/', update_ticket_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_ticket_update_invalid_no_park_id(self):
        ticket_date = self.park.start + datetime.timedelta(hours=1)

        update_ticket_data = {
            "date": ticket_date.isoformat()
        }

        response = self.client.patch('/api/user/ticket/', update_ticket_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            'park_id': [
                'This field is required.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_park_update_invalid_park_belongs_to_other_user(self):
        existing2_user_data = {
            "email": "existing2@user.com",
            "first_name": "Existing",
            "last_name": "User",
            "phone": "3753753755"
        }

        user2 = User.objects.create(**existing2_user_data)
        user2.set_password("defaultpassword")
        user2.save()

        user2_token = Token.objects.create(user=user2)

        ticket_date = self.park.start + datetime.timedelta(hours=30)

        update_ticket_data = {
            "park_id": self.park.pk,
            "date": ticket_date.isoformat()
        }

        response = self.client.patch('/api/user/ticket/', update_ticket_data, HTTP_AUTHORIZATION='Token ' + user2_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            'non_field_errors': [
                'The user does not own this park.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_park_update_invalid_park_dne(self):
        ticket_date = self.park.start + datetime.timedelta(hours=1)

        update_ticket_data = {
            "park_id": 99,
            "date": ticket_date.isoformat()
        }

        response = self.client.patch('/api/user/ticket/', update_ticket_data, HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            'park_id': [
                'Park with pk 99 does not exist.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_ticket_update_not_authenticated(self):
        ticket_date = self.park.start + datetime.timedelta(hours=1)

        update_ticket_data = {
            "park_id": self.park.pk,
            "date": ticket_date.isoformat(),
        }

        response = self.client.patch('/api/user/ticket/', update_ticket_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "detail": "Authentication credentials were not provided."
        }

        # verify response is correct
        self.assertEqual(response.status_code, 401, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")
