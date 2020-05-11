from django.test import TestCase, Client
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
import json

from api.models import User, PasswordResetToken

class PasswordResetTestCase(TestCase):
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

    #=== CREATE RESET TOKEN ===# 
    def test_create_valid(self):
        create_data = {
            "email": self.user.email
        }

        response = self.client.post('/api/user/password_reset/create/', create_data)
        response_content = json.loads(response.content)

        correct_response_content = {}

        # verify response is correct
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_content, correct_response_content)

        # verify password reset token was created
        try:
            reset_token = PasswordResetToken.objects.get(user=self.user)
        except:
            self.assertTrue(False, msg="PasswordResetToken was not created.")

    def test_create_invalid(self):
        create_data = {
            "email": "fake@user.com"
        }

        response = self.client.post('/api/user/password_reset/create/', create_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            'email': [
                'A user with the specified email does not exist.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_content, correct_response_content)

        # verify password reset token was not created
        reset_tokens = PasswordResetToken.objects.all()

        self.assertEqual(len(reset_tokens), 0)

    #=== VALIDATE RESET TOKEN ===#
    def test_validate_valid(self):
        # create reset token
        response = self.client.post('/api/user/password_reset/create/', {"email": self.user.email})

        reset_token = PasswordResetToken.objects.get(user=self.user)

        validate_data = {
            "email": self.user.email,
            "token": reset_token.token
        }

        response = self.client.post('/api/user/password_reset/validate_token/', validate_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": self.user.email,
            "token": reset_token.token
        }

        # verify response is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content, correct_response_content)

    def test_validate_invalid_token(self):
        # create reset token
        response = self.client.post('/api/user/password_reset/create/', {"email": self.user.email})

        reset_token = PasswordResetToken.objects.get(user=self.user)

        validate_data = {
            "email": self.user.email,
            "token": "123456"
        }

        response = self.client.post('/api/user/password_reset/validate_token/', validate_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            'attempts': ['2'],
            'error': [
                'Invalid token provided.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_content, correct_response_content)

    def test_validate_out_of_attempts(self):
        # create reset token
        response = self.client.post('/api/user/password_reset/create/', {"email": self.user.email})

        reset_token = PasswordResetToken.objects.get(user=self.user)

        validate_data = {
            "email": self.user.email,
            "token": "123456"
        }

        # fail the 3 allotted attempts
        for i in reversed(range(0, 3)):
            response = self.client.post('/api/user/password_reset/validate_token/', validate_data)
            response_content = json.loads(response.content)

            correct_response_content = {
                'attempts': [str(i)],
                'error': [
                    'Invalid token provided.'
                ]
            }

            # verify response is correct
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_content, correct_response_content)

        # try to validate with 0 attempts remaining
        response = self.client.post('/api/user/password_reset/validate_token/', validate_data)
        response_content = json.loads(response.content)
        
        correct_response_content = {
            'token': [
                'Too many attempts to reset password using the current token.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_content, correct_response_content)

    def test_reset_valid(self):
        # create reset token
        response = self.client.post('/api/user/password_reset/create/', {"email": self.user.email})

        reset_token = PasswordResetToken.objects.get(user=self.user)

        reset_data = {
            "email": self.user.email,
            "token": reset_token.token,
            "password": "newdefaultpassword",
            "password2": "newdefaultpassword"
        }

        response = self.client.post('/api/user/password_reset/reset/', reset_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "email": self.user.email,
            "token": self.user_token.key
        }

        # verify response is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content, correct_response_content)

        # verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newdefaultpassword"), msg="User instance did not have correct password.")

        # verify reset token was removed
        reset_tokens = PasswordResetToken.objects.all()
        self.assertEqual(len(reset_tokens), 0, msg="Reset token was not removed.")

    def test_reset_invalid_passwords_do_not_match(self):
        # create reset token
        response = self.client.post('/api/user/password_reset/create/', {"email": self.user.email})

        reset_token = PasswordResetToken.objects.get(user=self.user)

        reset_data = {
            "email": self.user.email,
            "token": reset_token.token,
            "password": "newdefaultpassword",
            "password2": "newdefaultpassword2"
        }

        response = self.client.post('/api/user/password_reset/reset/', reset_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "non_field_errors": [
                "Passwords must match."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_content, correct_response_content)

        # verify password was not changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("defaultpassword"), msg="User instance did not have correct password.")

    def test_reset_invalid_token(self):
        # create reset token
        response = self.client.post('/api/user/password_reset/create/', {"email": self.user.email})

        reset_token = PasswordResetToken.objects.get(user=self.user)

        reset_data = {
            "email": self.user.email,
            "token": "123456",
            "password": "newdefaultpassword",
            "password2": "newdefaultpassword"
        }

        response = self.client.post('/api/user/password_reset/reset/', reset_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            'attempts': ['2'],
            'error': [
                'Invalid token provided.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_content, correct_response_content)

        # verify password was not changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("defaultpassword"), msg="User instance did not have correct password.")

    def test_reset_password_invalid(self):
        # create reset token
        response = self.client.post('/api/user/password_reset/create/', {"email": self.user.email})

        reset_token = PasswordResetToken.objects.get(user=self.user)

        reset_data = {
            "email": self.user.email,
            "token": reset_token.token,
            "password": "",
            "password2": "updatedpassword"
        }

        response = self.client.post('/api/user/password_reset/reset/', reset_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password": [
                "This field may not be blank."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify password was not changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("defaultpassword"), msg="User instance did not have correct password.")

        reset_data = {
            "email": self.user.email,
            "token": reset_token.token,
            "password": "updatedpassword",
            "password2": ""
        }

        response = self.client.post('/api/user/password_reset/reset/', reset_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password2": [
                "This field may not be blank."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify password was not changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("defaultpassword"), msg="User instance did not have correct password.")

        reset_data = {
            "email": self.user.email,
            "token": reset_token.token,
            "password": "",
            "password2": ""
        }

        response = self.client.post('/api/user/password_reset/reset/', reset_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            'password': [
                'This field may not be blank.'
            ],
            'password2': [
                'This field may not be blank.'
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify password was not changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("defaultpassword"), msg="User instance did not have correct password.")

        reset_data = {
            "email": self.user.email,
            "token": reset_token.token,
            "password": "password",
            "password2": "password"
        }

        response = self.client.post('/api/user/password_reset/reset/', reset_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password": [
                "This password is too common."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify password was not changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("defaultpassword"), msg="User instance did not have correct password.")

        reset_data = {
            "email": self.user.email,
            "token": reset_token.token,
            "password": "imshort",
            "password2": "imshort"
        }

        response = self.client.post('/api/user/password_reset/reset/', reset_data)
        response_content = json.loads(response.content)

        correct_response_content = {
            "password": [
                "This password is too short. It must contain at least 8 characters."
            ]
        }

        # verify response is correct
        self.assertEqual(response.status_code, 400, msg="Invalid response status code.")
        self.assertEqual(response_content, correct_response_content, msg="Invalid response content.")

        # verify password was not changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("defaultpassword"), msg="User instance did not have correct password.")

        reset_data = {
            "email": self.user.email,
            "token": reset_token.token,
            "password": "pass",
            "password2": "pass"
        }

        response = self.client.post('/api/user/password_reset/reset/', reset_data)
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

        # verify password was not changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("defaultpassword"), msg="User instance did not have correct password.")