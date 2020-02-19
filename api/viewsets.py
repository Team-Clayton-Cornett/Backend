from .models import Garage, User, Park, Ticket
from .serializers import  GarageSerializer, UserSerializer, UserRegisterSerializer, PasswordSerializer, TicketSerializer, ParkSerializer
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.utils.dateparse import parse_datetime
from django.forms.models import model_to_dict
import re
import datetime

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

    @action(detail=False, methods=['post'])
    def create_user_ticket(self, request):
        try:
            park = Park.objects.get(pk=request.data['park_id'])
        except:
            return Response('Park with pk ' + str(pk) + ' does not exist.',
                            status=status.HTTP_400_BAD_REQUEST)

        if park.user != request.user:
            return Response('The user does not own this park.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get('date'):
            date = serializer.validated_data.get('date')
            if date < park.start or park.end != None and date > park.end:
                return Response('The date of the ticket must be during park time.',
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

    @action(detail=True, methods=['get'])
    def get_user(self, request):
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        else:
            return Response('You must be logged in to perform this action.',
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'])
    def update_user(self, request):
        instance = request.user

        if not request.user.is_authenticated:
            return Response('You must be logged in to perform this action.',
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
