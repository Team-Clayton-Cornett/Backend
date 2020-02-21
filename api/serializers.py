from rest_framework import serializers
import datetime
from django.core import exceptions
from django.contrib.auth.password_validation import validate_password as django_validate_password
from rest_framework.fields import CurrentUserDefault
import re

from .models import Probability, DayProbability, Garage, Ticket, Park, User, PasswordResetToken

class ProbabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Probability
        fields = ('time', 'probability')

class DayProbabilitySerializer(serializers.ModelSerializer):
    probability = serializers.SerializerMethodField('get_probability_data')

    def get_probability_data(self, obj):
        time = self.context.get('time', None)

        if time:
            try:
                format = "%H:%M"
                time_object = datetime.datetime.strptime(time, format)
            except:
                return None

            minutes = time_object.hour * 60 + time_object.minute

            serializer = ProbabilitySerializer(obj.probability[minutes // 15])
            return serializer.data
        else:
            serializer = ProbabilitySerializer(obj.probability, many=True)
            return serializer.data
    
    class Meta:
        model = DayProbability
        fields = ('day_of_week', 'probability')

class GarageSerializer(serializers.ModelSerializer):
    probability = serializers.SerializerMethodField('get_probability_data')
    
    def get_probability_data(self, obj):
        day_of_week = self.context.get('day_of_week', None)

        if day_of_week:
            days_of_week = {
                'Sun': 0,
                'Mon': 1,
                'Tue': 2,
                'Wed': 3,
                'Thu': 4,
                'Fri': 5,
                'Sat': 6,
            }
            
            if day_of_week == 'None' or day_of_week not in days_of_week:
                return None
            else:
                serializer = DayProbabilitySerializer(obj.probability[days_of_week[day_of_week]], context=self.context)
                return serializer.data
        else:
            serializer = DayProbabilitySerializer(obj.probability, many=True, context=self.context)
            return serializer.data

    class Meta:
        model = Garage
        fields = ('pk', 'name', 'start_enforce_time', 'end_enforce_time', 'enforced_on_weekends', 'probability', 'latitude', 'longitude')

class GarageSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garage
        fields = ('pk', 'name')

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('date', 'day_of_week')
        read_only_fields = ('day_of_week',)

class ParkSerializer(serializers.ModelSerializer):
    garage = GarageSimpleSerializer(read_only=True)
    garage_id = serializers.PrimaryKeyRelatedField(queryset=Garage.objects.all(), source='garage', write_only=True)
    ticket = TicketSerializer(required=False, allow_null=True, default=None)
    end = serializers.DateTimeField(required=False, allow_null=True, default=None)

    class Meta:
        model = Park
        fields = ('pk', 'start', 'end', 'ticket', 'garage', 'garage_id', 'user')
        read_only_fields = ('garage', 'pk')

class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    password2 = serializers.CharField()

    def validate(self, data):
        if data.get('password'):
            if not data.get('password2'):
                raise serializers.ValidationError("Password confirmation not provided.")

            if data.get('password') != data.get('password2'):
                raise serializers.ValidationError("Passwords must match.")

            errors = dict()
            try:
                # validate the password and catch the exception
                django_validate_password(password=data.get('password'), user=self.context.get('user'))
            # the exception raised here is different than serializers.ValidationError
            except exceptions.ValidationError as e:
                errors['password'] = list(e.messages)

            if errors:
                raise serializers.ValidationError(errors)

        return data

class UserSerializer(serializers.ModelSerializer):
    park = ParkSerializer(many=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'password')

    def validate_email(self, email):
        existing = User.objects.filter(email=email).first()
        if existing:
            raise serializers.ValidationError("Someone with that email address already exists.")

        return email

class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    phone = serializers.CharField(max_length=17, required=False)
    password = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'park', 'password', 'password2')

    def validate_email(self, email):
        existing = User.objects.filter(email=email).first()
        if existing:
            raise serializers.ValidationError("Someone with that email address already exists.")

        return email

    def validate_phone(self, phone):
        if not re.match(r'^\+?1?\d{9,15}$', phone):
            raise serializers.ValidationError("Invalid phone number format.")

        return phone

class PasswordResetTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordResetToken
        fields = ('user', 'token', 'expires', 'attempts')

class GeneratePasswordResetTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        existing = User.objects.filter(email=email).first()

        if not existing:
            raise serializers.ValidationError("A user with the specified email does not exist.")

        return email

class ValidateResetTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=6)
    email = serializers.EmailField()

    def validate(self, data):
        errors = dict()

        user = User.objects.get(email=data.get('email'))

        if user:
            if not hasattr(user, 'passwordresettoken'):
                errors['non_field_errors'] = "User has not generated a password reset token."
            else:
                if user.passwordresettoken.expires < datetime.datetime.now():
                    errors['token'] = "Password reset token has expired."
                elif user.passwordresettoken.attempts <= 0:
                    errors['token'] = "Too many attempts to reset password using the current token."
        else:
            errors['email'] = "A user with the specified email does not exist."

        if errors:
            raise serializers.ValidationError(errors)

        return data

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6)
    password = serializers.CharField()
    password2 = serializers.CharField()

    def validate(self, data):
        errors = dict()

        user = User.objects.get(email=data.get('email'))

        if user:
            token_serializer = ValidateResetTokenSerializer(data={'email': data.get('email', None), 'token': data.get('token', None)})
            token_serializer.is_valid(raise_exception=True)

            if data.get('token', None) != user.passwordresettoken.token:
                user.passwordresettoken.attempts -= 1
                user.passwordresettoken.save()

                raise serializers.ValidationError({'error': 'Invalid token provided.', 'attempts': user.passwordresettoken.attempts})

            password_serializer = PasswordSerializer(data={'password': data.get('password', None), 'password2': data.get('password2', None)}, context={'user': user})
            password_serializer.is_valid(raise_exception=True)

        return data
