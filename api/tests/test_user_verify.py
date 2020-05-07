from django.test import TestCase, Client
from rest_framework.test import APIClient
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
import json

from api.models import User

class UserVerifyTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        existing_user_data = {
            "email": "existing@user.com",
            "first_name": "Existing",
            "last_name": "User",
            "phone": "5735735733"
        }

        self.existing_user = User.objects.create(**existing_user_data)
        self.existing_user.set_password("defaultpassword")
        self.existing_user.save()

        self.existing_user_token = Token.objects.create(user=self.existing_user)

    def test_user_verify_valid_token(self):
        response = self.client.post('/api/user/verify/', {}, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = True

        # verify response is correct
        self.assertEqual(response.status_code, 200, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_verify_invalid_token(self):
        response = self.client.post('/api/user/verify/', {}, HTTP_AUTHORIZATION='Token b54536d86ffaa67e0cefc50b362b95aa1a7bcasd')
        response_content = json.loads(response.content)

        correct_response_content = {
            'detail': 'Invalid token.'
        }

        # verify response is correct
        self.assertEqual(response.status_code, 401, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_verify_no_token(self):
        response = self.client.post('/api/user/verify/', {})
        response_content = json.loads(response.content)

        correct_response_content = {
            'detail': 'Authentication credentials were not provided.'
        }

        # verify response is correct
        self.assertEqual(response.status_code, 401, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")