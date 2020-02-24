from .models import Garage, User, Park, Ticket, PasswordResetToken
from .serializers import  GarageSerializer, UserSerializer, UserRegisterSerializer, PasswordSerializer, TicketSerializer, ParkSerializer, GeneratePasswordResetTokenSerializer, PasswordResetSerializer, ValidateResetTokenSerializer
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.utils.dateparse import parse_datetime
from django.utils.html import strip_tags
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from django.core.mail import send_mail
from datetime import datetime, timedelta
import re
import random
import string

from .permissions import IsAuthenticatedOrPost

class GarageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Garage.objects.all()
    serializer_class = GarageSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super(GarageViewSet, self).get_serializer_context()
        
        if 'day_of_week' in self.kwargs:
            if re.match('^\d\d:\d\d$', self.kwargs['day_of_week']):
                context['time'] = self.kwargs['day_of_week']
            else:
                context['day_of_week'] = self.kwargs['day_of_week']
        if 'time' in self.kwargs:
            context['time'] = self.kwargs['time']

        return context

class ParkViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ParkSerializer

    @action(detail=True, methods=['get'])
    def get_user_parks(self, request):
        if request.data.get('pk'):
            park = Park.objects.get(pk=request.data['pk'])

            if park.user != request.user:
                return Response('The user does not own the specified park.',
                                status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(park)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, headers=headers)

        user_parks = request.user.parks()
        serializer = self.get_serializer(user_parks, many=True)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_user_park(self, request):
        request.data['user'] = request.user.pk

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        park = self.create(serializer.validated_data)

        # create new serializer instance so that the pk will be returned
        new_serializer = self.get_serializer(park)

        headers = self.get_success_headers(serializer.data)
        return Response(new_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['patch'])
    def update_user_park(self, request):
        try:
            instance = Park.objects.get(pk=request.data['pk'])
        except:
            return Response('Park with pk ' + str(pk) + ' does not exist.',
                            status=status.HTTP_400_BAD_REQUEST)

        # create serializer instance and validate new data
        if instance.user != request.user:
            return Response('The user does not own this park.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if instance.ticket:
            if serializer.validated_data.get('end'):
                end = serializer.validated_data.get('end')
                if end < instance.ticket.date:
                    return Response('The end date of the park must be after the reported ticket date.',
                            status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)

    def create(self, validated_data):
        park = Park.objects.create(**validated_data)

        return park

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer

    @action(detail=False, methods=['post', 'patch'])
    def create_user_ticket(self, request):
        try:
            park = Park.objects.get(pk=request.data['park_id'])
        except:
            return Response({'park_id': ['Park with pk ' + str(pk) + ' does not exist.']},
                            status=status.HTTP_400_BAD_REQUEST)

        if park.user != request.user:
            return Response({'non_field_errors': ['The user does not own this park.']},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get('date'):
            date = serializer.validated_data.get('date')
            if date < park.start or park.end != None and date > park.end:
                return Response({'date': ['The date of the ticket must be during park time.']},
                            status=status.HTTP_400_BAD_REQUEST)

        ticket = Ticket(**serializer.validated_data)

        park.ticket = ticket
        park.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED, headers=headers)

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrPost]
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()

        return queryset

    @action(detail=False, methods=['post'])
    def verify_token(self, request):
        try:
            token = Token.objects.get(key=request.data['token'])

            if token:
                return Response(True, status=status.HTTP_200_SUCCESS)
            
            return Response(False, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response(False, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=True, methods=['get'])
    def get_user(self, request):
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        else:
            return Response({'non_field_errors': ['You must be logged in to perform this action.']},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'])
    def update_user(self, request):
        instance = request.user

        if not request.user.is_authenticated:
            return Response({'non_field_errors': ['You must be logged in to perform this action.']},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('password'):
            password_data = {'password': request.data.get('password')}
            if request.data.get('password2'):
                password_data['password2'] = request.data.get('password2')

            password_serializer = PasswordSerializer(data=password_data, context={'user': instance})
            password_serializer.is_valid(raise_exception=True)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        if request.data.get('password'):
            instance.set_password(serializer.validated_data.get('password'))
            instance.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)

    @action(detail=False, methods=['post'])
    def create_user(self, request):
        if request.data.get('password'):
            password_data = {'password': request.data.get('password')}
            if request.data.get('password2'):
                password_data['password2'] = request.data.get('password2')

            password_serializer = PasswordSerializer(data=password_data, context={'user': User(request.data)})
            password_serializer.is_valid(raise_exception=True)

        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.create(serializer.validated_data)

        token, created = Token.objects.get_or_create(user=user)

        headers = self.get_success_headers(serializer.data)
        return Response({'user': serializer.data, 'token': token.key}, status=status.HTTP_201_CREATED, headers=headers)

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User(**validated_data)
        user.set_password(validated_data.get('password'))
        user.save()

        return user

class PasswordResetViewSet(viewsets.ModelViewSet):
    permission_classes = []
    serializer_class = PasswordResetSerializer


    @action(detail=False, methods=['post'])
    def generate_password_reset_token(self, request):
        serializer = GeneratePasswordResetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data['email'])
        token = ''.join(random.choice((string.ascii_uppercase + string.digits).replace('O', '')) for _ in range(6))
        expires = datetime.now() + timedelta(hours=1)
        attempts = 3

        if hasattr(user, 'passwordresettoken'):
            user.passwordresettoken.token = token
            user.passwordresettoken.expires = expires
            user.passwordresettoken.attempts = attempts
            user.passwordresettoken.save()
        else:
            password_reset_token = PasswordResetToken.objects.create(user=user, token=token, expires=expires, attempts=attempts)

        # generate email content
        email_template = render_to_string('password_reset_email.html', {'token': token})
        # Remove html tags and continuous whitespaces
        text_email = re.sub('[ \t]+', ' ', strip_tags(email_template))
        # Strip single spaces in the beginning of each line
        text_email = text_email.replace('\n ', '\n').strip()
        subject = "Password Reset for Clayton Cornett App"
        sender = "no-reply@claytoncornett.tk"
        to = [user.email]

        try:
            send_mail(subject=subject, message=text_email, from_email=sender, recipient_list=to, html_message=email_template, fail_silently=False)
        except:
            return Response({'non_field_errors': ['Failed to send password reset email.']}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response({}, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['post'])
    def validate_password_reset_token(self, request):
        serializer = ValidateResetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data['email'])

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.validated_data, headers=headers)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data['email'])

        user.set_password(serializer.validated_data.get('password'))
        user.save()

        user.passwordresettoken.delete()

        token, created = Token.objects.get_or_create(user=user)

        headers = self.get_success_headers(serializer.data)
        return Response({'email': serializer.validated_data['email'], 'token': token.key}, headers=headers)
