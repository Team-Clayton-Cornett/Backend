from django.test import TestCase, Client
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
import json

from api.models import User

# Create your tests here.
class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        existing_user_data = {
            "email": "existing@user.com",
            "first_name": "Existing",
            "last_name": "User",
            "phone": "5735735733",
            "password": "defaultpassword"
        }

        self.user = User.objects.create(**existing_user_data)
        self.user.set_password("defaultpassword")
        self.user.save()

    def test_login_valid(self):
        login_data = {
            "username": "existing@user.com",
            "password": "defaultpassword"
        }

        response = self.client.post('/api/login/', login_data)
        response_content = json.loads(response.content)

        # verify response is correct
        self.assertEqual(response.status_code, 200)

        # verify token is created
        tokens = Token.objects.all()
        self.assertEqual(len(tokens), 1)

        token = Token.objects.first()

        correct_response_content = {
            "token": token.key
        }

        # verify response content is correct
        self.assertEqual(response_content, correct_response_content)

    def test_login_invalid_username(self):
        login_data = {
            "username": "invalid@user.com",
            "password": "defaultpassword"
        }

        response = self.client.post('/api/login/', login_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            'non_field_errors': [
                'Unable to log in with provided credentials.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_content, correct_response_content)

        # verify token is not created
        tokens = Token.objects.all()
        self.assertEqual(len(tokens), 0)

    def test_login_invalid_password(self):
        login_data = {
            "username": "existing@user.com",
            "password": "default"
        }

        response = self.client.post('/api/login/', login_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            'non_field_errors': [
                'Unable to log in with provided credentials.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_content, correct_response_content)

        # verify token is not created
        tokens = Token.objects.all()
        self.assertEqual(len(tokens), 0)

    def test_login_invalid(self):
        login_data = {
            "username": "invalid@user.com",
            "password": "default"
        }

        response = self.client.post('/api/login/', login_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            'non_field_errors': [
                'Unable to log in with provided credentials.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_content, correct_response_content)

        # verify token is not created
        tokens = Token.objects.all()
        self.assertEqual(len(tokens), 0)

