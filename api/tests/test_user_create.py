from django.test import TestCase, Client
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
import json

from api.models import User

class UserCreateTestCase(TestCase):
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

    def test_user_create_valid(self):
        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_user_content = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "1234567890"
        }

        # verify response is correct
        self.assertEqual(response.status_code, 201, msg="Invalid response status code.")
        self.assertEqual(response_content['user'], correct_response_user_content, msg="Invalid response content.")

        # verify user was created
        self.assertEqual(User.objects.filter(email="new@user.com").count(), 1, msg="User instance was not created in database.")
        new_user = User.objects.get(email="new@user.com")

        # verify created user has correct data
        new_user_data = model_to_dict(new_user, fields=['email', 'first_name', 'last_name', 'phone'])
        self.assertEqual(new_user_data, correct_response_user_content, msg="User instance did not have correct data.")

        # verify created user has correct password
        self.assertTrue(new_user.check_password("defaultpassword"), msg="User instance did not have correct password.")

        # verify token for user was created
        self.assertEqual(Token.objects.filter(user=new_user).count(), 1, msg="Token was not created for new user.")
        new_token = Token.objects.get(user=new_user)

        # verify response had correct token data
        self.assertEqual(response_content['token'], new_token.key)

    def test_user_create_valid_no_phone(self):
        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "User",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_user_content = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "User"
        }

        # verify response is correct
        self.assertEqual(response.status_code, 201, msg="Invalid response status code.")
        self.assertEqual(response_content['user'], correct_response_user_content, msg="Invalid response content.")

        # verify user was created
        self.assertEqual(User.objects.filter(email="new@user.com").count(), 1, msg="User instance was not created in database.")
        new_user = User.objects.get(email="new@user.com")

        # verify created user has correct data
        new_user_data = model_to_dict(new_user, fields=['email', 'first_name', 'last_name'])
        self.assertEqual(new_user_data, correct_response_user_content, msg="User instance did not have correct data.")

        # verify user phone data is correct
        self.assertEqual(new_user.phone, '', msg="User instance did not have blank phone number.")

        # verify created user has correct password
        self.assertTrue(new_user.check_password("defaultpassword"), msg="User instance did not have correct password.")

        # verify token for user was created
        self.assertEqual(Token.objects.filter(user=new_user).count(), 1, msg="Token was not created for new user.")
        new_token = Token.objects.get(user=new_user)

        # verify response had correct token data
        self.assertEqual(response_content['token'], new_token.key)

    def test_user_create_passwords_do_not_match(self):
        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "differentpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "non_field_errors": [
                "Passwords must match."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_create_user_already_exists(self):
        create_user_data = {
            "email": "existing@user.com",
            "first_name": "Existing",
            "last_name": "User",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": [
                "Someone with that email address already exists."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_create_user_no_email(self):
        create_user_data = {
            "first_name": "New",
            "last_name": "User",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": [
                "This field is required."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_create_user_no_first_name(self):
        create_user_data = {
            "email": "new@user.com",
            "last_name": "User",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "first_name": [
                "This field is required."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_create_user_no_last_name(self):
        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "last_name": [
                "This field is required."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_create_user_no_password(self):
        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "1234567890",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password": [
                "This field is required."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_create_user_no_password2(self):
        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "1234567890",
            "password": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password2": [
                "This field is required."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_create_user_email_invalid(self):
        create_user_data = {
            "email": "new@user",
            "first_name": "New",
            "last_name": "User",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": [
                "Enter a valid email address."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")
        
        create_user_data = {
            "email": "",
            "first_name": "New",
            "last_name": "User",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": [
                "This field may not be blank."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_create_user_first_name_invalid(self):
        create_user_data = {
            "email": "new@user.com",
            "first_name": "ThisFirstNameIsLongerThanThirtyCharacters",
            "last_name": "User",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "first_name": [
                "Ensure this field has no more than 30 characters."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        create_user_data = {
            "email": "new@user.com",
            "first_name": "",
            "last_name": "User",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "first_name": [
                "This field may not be blank."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_create_user_last_name_invalid(self):
        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "ThisLastNameAbsolutelyHasWayMoreThanOneHundredAndFiftyCharactersYouMayNotBelieveItButItReallyTrulyDoesContainThanOneHundredAndFiftyCharactersInItsField",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "last_name": [
                "Ensure this field has no more than 150 characters."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "last_name": [
                "This field may not be blank."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_create_user_phone_invalid(self):
        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "12345",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "phone": [
                "Invalid phone number format."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_create_user_password_invalid(self):
        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "1234567890",
            "password": "",
            "password2": "defaultpassword"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password": [
                "This field may not be blank."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": ""
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password2": [
                "This field is required."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "1234567890",
            "password": "",
            "password2": ""
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password": [
                "This field may not be blank."
            ],
            "password2": [
                "This field may not be blank."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "1234567890",
            "password": "password",
            "password2": "password"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password": [
                "This password is too common."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "1234567890",
            "password": "imshort",
            "password2": "imshort"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password": [
                "This password is too short. It must contain at least 8 characters."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        create_user_data = {
            "email": "new@user.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "1234567890",
            "password": "pass",
            "password2": "pass"
        }

        response = self.client.post('/api/user/', create_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password": [
                "This password is too short. It must contain at least 8 characters.",
                "This password is too common."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")