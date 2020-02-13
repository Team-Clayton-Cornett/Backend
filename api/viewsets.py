from .models import Garage
from .serializers import  GarageSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
import re

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
        
