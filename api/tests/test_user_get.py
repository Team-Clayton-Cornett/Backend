from django.test import TestCase, Client
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
import json

from api.models import User

# Create your tests here.
class UserGetTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        existing_user_data = {
            "email": "existing@user.com",
            "first_name": "Existing",
            "last_name": "User",
            "phone": "5735735733",
            "password": "defaultpassword"
        }

        self.existing_user = User.objects.create(**existing_user_data)
        self.existing_user_token = Token.objects.create(user=self.existing_user)

    def test_user_get_valid(self):
        headers = {
            "HTTP_AUTHORIZATION": "Token " + self.existing_user_token.key
        }

        response = self.client.get('/api/user/', **headers)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": "existing@user.com",
            "first_name": "Existing",
            "last_name": "User",
            "phone": "5735735733"
        }

        # verify response is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content, correct_response_content)

    def test_user_get_invalid_token(self):
        headers = {
            "HTTP_AUTHORIZATION": "Token InvalidToken12345"
        }

        response = self.client.get('/api/user/', **headers)
        response_content = json.loads(response.content)

        correct_response_content = {
            "detail": "Invalid token."
        }

        # verify response is correct
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_content, correct_response_content)

    def test_user_get_no_token(self):
        response = self.client.get('/api/user/')
        response_content = json.loads(response.content)

        correct_response_content = {
            "detail": "Authentication credentials were not provided."
        }

        # verify response is correct
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_content, correct_response_content)
