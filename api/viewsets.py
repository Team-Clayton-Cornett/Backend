from .models import Garage, User, Park
from .serializers import  GarageSerializer, UserSerializer, UserRegisterSerializer, PasswordSerializer
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
import re
import datetime

from .permissions import IsAuthenticatedOrPost
from .models import User

class GarageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Garage.objects.all()
    serializer_class = GarageSerializer
    # permission_classes = [IsAuthenticated]

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

    @action(detail=True, methods=['patch'])
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

    @action(detail=True, methods=['post'])
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
