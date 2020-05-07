from django.test import TestCase, Client
from rest_framework.test import APIClient
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
import json

from api.models import User

class UserUpdateTestCase(TestCase):
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

    def test_user_update_valid_full(self):
        update_user_data = {
            "email": "updated@user.com",
            "first_name": "Updated",
            "last_name": "User",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": "updated@user.com",
            "first_name": "Updated",
            "last_name": "User",
            "phone": "1234567890"
        }

        # verify response is correct
        self.assertEqual(response.status_code, 200, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify user was updated
        self.assertEqual(User.objects.filter(email="updated@user.com").count(), 1, msg="User instance was not updated in database.")
        updated_user = User.objects.get(email="updated@user.com")

        # verify updated user has correct data
        updated_user_data = model_to_dict(updated_user, fields=['email', 'first_name', 'last_name', 'phone'])
        self.assertEqual(updated_user_data, correct_response_content, msg="User instance did not have correct data.")

        # verify updated user has correct password
        self.assertTrue(updated_user.check_password("defaultpassword"), msg="User instance did not have correct password.")

    def test_user_update_valid_email(self):
        update_user_data = {
            "email": "updated@user.com"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": "updated@user.com",
            "first_name": "Existing",
            "last_name": "User",
            "phone": "5735735733"
        }

        # verify response is correct
        self.assertEqual(response.status_code, 200, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify user was updated
        self.assertEqual(User.objects.filter(email="updated@user.com").count(), 1, msg="User instance was not updated in database.")
        updated_user = User.objects.get(email="updated@user.com")

        # verify updated user has correct data
        updated_user_data = model_to_dict(updated_user, fields=['email', 'first_name', 'last_name', 'phone'])
        self.assertEqual(updated_user_data, correct_response_content, msg="User instance did not have correct data.")

        # verify updated user has correct password
        self.assertTrue(updated_user.check_password("defaultpassword"), msg="User instance did not have correct password.")

    def test_user_update_user_email_invalid(self):
        update_user_data = {
            "email": "new@user"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": [
                "Enter a valid email address."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")
        
        update_user_data = {
            "email": ""
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": [
                "This field may not be blank."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_update_user_email_already_exists(self):
        existing_user_data = {
            "email": "updated@user.com",
            "first_name": "Updated",
            "last_name": "User",
            "phone": "5735735733"
        }

        User.objects.create(**existing_user_data)
        
        update_user_data = {
            "email": "updated@user.com"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": [
                "user with this email address already exists."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_update_valid_first_name(self):
        update_user_data = {
            "first_name": "Updated"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": "existing@user.com",
            "first_name": "Updated",
            "last_name": "User",
            "phone": "5735735733"
        }

        # verify response is correct
        self.assertEqual(response.status_code, 200, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify user was updated
        self.assertEqual(User.objects.filter(email="existing@user.com").count(), 1, msg="User instance was not updated in database.")
        updated_user = User.objects.get(email="existing@user.com")

        # verify updated user has correct data
        updated_user_data = model_to_dict(updated_user, fields=['email', 'first_name', 'last_name', 'phone'])
        self.assertEqual(updated_user_data, correct_response_content, msg="User instance did not have correct data.")

        # verify updated user has correct password
        self.assertTrue(updated_user.check_password("defaultpassword"), msg="User instance did not have correct password.")

    def test_user_update_user_first_name_invalid(self):
        update_user_data = {
            "first_name": "ThisFirstNameIsLongerThanThirtyCharacters",
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "first_name": [
                "Ensure this field has no more than 30 characters."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_update_valid_last_name(self):
        update_user_data = {
            "last_name": "User2"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": "existing@user.com",
            "first_name": "Existing",
            "last_name": "User2",
            "phone": "5735735733"
        }

        # verify response is correct
        self.assertEqual(response.status_code, 200, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify user was updated
        self.assertEqual(User.objects.filter(email="existing@user.com").count(), 1, msg="User instance was not updated in database.")
        updated_user = User.objects.get(email="existing@user.com")

        # verify updated user has correct data
        updated_user_data = model_to_dict(updated_user, fields=['email', 'first_name', 'last_name', 'phone'])
        self.assertEqual(updated_user_data, correct_response_content, msg="User instance did not have correct data.")

        # verify updated user has correct password
        self.assertTrue(updated_user.check_password("defaultpassword"), msg="User instance did not have correct password.")

    def test_user_update_user_last_name_invalid(self):
        update_user_data = {
            "last_name": "ThisLastNameAbsolutelyHasWayMoreThanOneHundredAndFiftyCharactersYouMayNotBelieveItButItReallyTrulyDoesContainThanOneHundredAndFiftyCharactersInItsField",
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "last_name": [
                "Ensure this field has no more than 150 characters."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_update_valid_phone(self):
        update_user_data = {
            "phone": "1234567890"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": "existing@user.com",
            "first_name": "Existing",
            "last_name": "User",
            "phone": "1234567890"
        }

        # verify response is correct
        self.assertEqual(response.status_code, 200, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify user was updated
        self.assertEqual(User.objects.filter(email="existing@user.com").count(), 1, msg="User instance was not updated in database.")
        updated_user = User.objects.get(email="existing@user.com")

        # verify updated user has correct data
        updated_user_data = model_to_dict(updated_user, fields=['email', 'first_name', 'last_name', 'phone'])
        self.assertEqual(updated_user_data, correct_response_content, msg="User instance did not have correct data.")

        # verify updated user has correct password
        self.assertTrue(updated_user.check_password("defaultpassword"), msg="User instance did not have correct password.")

    def test_user_update_user_phone_invalid(self):
        update_user_data = {
            "phone": "12345"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "phone": [
                "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_update_valid_password(self):
        update_user_data = {
            "password": "updatedpassword",
            "password2": "updatedpassword"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": "existing@user.com",
            "first_name": "Existing",
            "last_name": "User",
            "phone": "5735735733"
        }

        # verify response is correct
        self.assertEqual(response.status_code, 200, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify user was updated
        self.assertEqual(User.objects.filter(email="existing@user.com").count(), 1, msg="User instance was not updated in database.")
        updated_user = User.objects.get(email="existing@user.com")

        # verify updated user has correct data
        updated_user_data = model_to_dict(updated_user, fields=['email', 'first_name', 'last_name', 'phone'])
        self.assertEqual(updated_user_data, correct_response_content, msg="User instance did not have correct data.")

        # verify updated user has correct password
        self.assertTrue(updated_user.check_password("updatedpassword"), msg="User instance did not have correct password.")

    def test_user_update_passwords_do_not_match(self):
        update_user_data = {
            "password": "updatedpassword",
            "password2": "differentpassword"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "non_field_errors": [
                "Passwords must match."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify password was not changed
        updated_user = User.objects.get(email="existing@user.com")
        self.assertTrue(updated_user.check_password("defaultpassword"), msg="User instance did not have correct password.")

    def test_user_update_not_authenticated(self):
        update_user_data = {
            "email": "updated@user.com",
            "first_name": "Updated",
            "last_name": "User",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.patch('/api/user/', update_user_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "detail": "Authentication credentials were not provided."
        }

        # verify response is correct
        self.assertEqual(response.status_code, 401, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_update_invalid_token(self):
        update_user_data = {
            "email": "updated@user.com",
            "first_name": "Updated",
            "last_name": "User",
            "phone": "1234567890",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION="Token b54536d86ffaa67e0cefc50b362b95aa1a7bcasd")
        response_content = json.loads(response.content)

        correct_response_content = {
            "detail": "Invalid token."
        }

        # verify response is correct
        self.assertEqual(response.status_code, 401, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_update_user_no_password2(self):
        update_user_data = {
            "password": "updatedpassword"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password2": [
                "This field is required."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

    def test_user_update_user_password_invalid(self):
        update_user_data = {
            "password": "",
            "password2": "updatedpassword"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password": [
                "This field may not be blank."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        update_user_data = {
            "password": "updatedpassword",
            "password2": ""
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password2": [
                "This field is required."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        update_user_data = {
            "password": "",
            "password2": ""
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password": [
                "This field may not be blank."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        update_user_data = {
            "password": "password",
            "password2": "password"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password": [
                "This password is too common."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        update_user_data = {
            "password": "imshort",
            "password2": "imshort"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password": [
                "This password is too short. It must contain at least 8 characters."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        update_user_data = {
            "password": "pass",
            "password2": "pass"
        }

        response = self.client.patch('/api/user/', update_user_data, HTTP_AUTHORIZATION='Token ' + self.existing_user_token.key)
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
