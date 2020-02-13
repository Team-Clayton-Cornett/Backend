from rest_framework import serializers
import datetime

from .models import Probability, DayProbability, Garage, Ticket, Park, User

class ProbabilitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Probability
        fields = ('time', 'probability')

class DayProbabilitySerializer(serializers.HyperlinkedModelSerializer):
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

class GarageSerializer(serializers.HyperlinkedModelSerializer):
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
        fields = ('name', 'start_enforce_time', 'end_enforce_time', 'enforced_on_weekends', 'probability', 'latitude', 'longitude')

class TicketSerializer(serializers.HyperlinkedModelSerializer):
    garage = GarageSerializer()

    class Meta:
        model = Ticket
        fields = ('date', 'day_of_week', 'garage')

class ParkSerializer(serializers.HyperlinkedModelSerializer):
    ticket = TicketSerializer()
    
    class Meta:
        model = Park
        fields = ('start', 'end', 'ticket')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    park = ParkSerializer(many=True)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'park')