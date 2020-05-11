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

        self.user_token = Token.objects.create(user=self.user)

    def test_logout_valid(self):
        response = self.client.post('/api/logout/', HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = True

        # verify response is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content, correct_response_content)

        # verify token is removed
        tokens = Token.objects.all()
        self.assertEqual(len(tokens), 0)

    def test_logout_invalid_invalid_token(self):
        response = self.client.post('/api/logout/', HTTP_AUTHORIZATION='Token InvalidToken12345')
        response_content = json.loads(response.content)

        correct_response_content = {
            "detail": "Invalid token."
        }

        # verify response is correct
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_content, correct_response_content)

        # verify token is not removed
        tokens = Token.objects.all()
        self.assertEqual(len(tokens), 1)

    def test_logout_invalid_not_authenticated(self):
        response = self.client.post('/api/logout/')
        response_content = json.loads(response.content)

        correct_response_content = {
            "detail": "Authentication credentials were not provided."
        }

        # verify response is correct
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_content, correct_response_content)

        # verify token is not removed
        tokens = Token.objects.all()
        self.assertEqual(len(tokens), 1)