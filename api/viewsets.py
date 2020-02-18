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
        user_parks = request.user.park
        serializer = self.get_serializer(user_parks, many=True, context={'details': True})

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def get_user_park(self, request, pk):
        user_parks = request.user.park

        try:
            serializer = self.get_serializer(user_parks[pk], context={'details': True})
            return Response(serializer.data)
        except:
            return Response('User does not have park with pk of ' + str(pk) + '.',
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def create_user_park(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_parks = request.user.park
        if user_parks is None:
            user_parks = [Park(**serializer.validated_data)]
        else:
            user_parks.append(Park(**serializer.validated_data))

        request.user.park = user_parks
        request.user.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['patch'])
    def update_user_park(self, request, pk):
        try:
            instance = request.user.park[pk]
        except:
            return Response('User does not have park with pk of ' + str(pk) + '.',
                            status=status.HTTP_400_BAD_REQUEST)

        # convert park instance to dict, rename garage & ticket to garage_id & ticket_id
        instance_dict = model_to_dict(instance, fields=['start', 'end', 'ticket', 'garage'])
        instance_dict['garage_id'] = instance_dict.pop('garage')
        instance_dict['ticket_id'] = instance_dict.pop('ticket')
        # update dictionary to new data from request.data
        instance_dict.update(request.data)

        # create serializer instance and validate new data
        serializer = self.get_serializer(data=instance_dict)
        serializer.is_valid(raise_exception=True)

        # create new Park instance and save to user.park array
        request.user.park[pk] = Park(**serializer.validated_data)
        request.user.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer

    @action(detail=True, methods=['get'])
    def get_user_unassigned_tickets(self, request):
        user_parks = request.user.park
        used_tickets = []

        for park in user_parks:
            if park.ticket != None:
                tickets.append(park.ticket_id)

        tickets = Ticket.objects.filter(user=request.user).exclude(pk__in=used_tickets).order_by('date')

        serializer = self.get_serializer(tickets, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def get_user_tickets(self, request):
        queryset = Ticket.objects.filter(user=request.user).order_by('date')
        serializer = self.get_serializer(queryset, many=True)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)

    @action(detail=False, methods=['post'])
    def create_user_ticket(self, request):
        request.data['user'] = request.user.pk

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket = self.create(serializer.validated_data)

        # create new serializer instance so that the pk will be returned
        new_serializer = self.get_serializer(ticket)

        headers = self.get_success_headers(serializer.data)
        return Response(new_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['patch'])
    def update_user_ticket(self, request):
        instance = Ticket.objects.get(pk=request.data['pk'])

        if instance.user != request.user:
            return Response('You are not the creator of this ticket.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        return Response(serializer.data)

    def create(self, validated_data):
        ticket = Ticket.objects.create(**validated_data)

        return ticket


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

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

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
