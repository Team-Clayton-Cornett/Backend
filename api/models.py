from djongo import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from .managers import UserManager

# choices for day_of_week
DAYS_OF_WEEK = (
    ('Sun', 'Sunday'),
    ('Mon', 'Monday'),
    ('Tue', 'Tuesday'),
    ('Wed', 'Wednesday'),
    ('Thu', 'Thursday'),
    ('Fri', 'Friday'),
    ('Sat', 'Saturday'),
)

class Probability(models.Model):
    # start time for the probability (15 minute duration). ie) 00:00 == 00:00 <= time < 00:15
    time = models.TimeField()
    # probability value. 0 <= value <= 1
    probability = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

class DayProbability(models.Model):
    # day of week enumeration. see DayOfWeekEnum above for values
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    # array/list of Probability. [0] = 00:00, [1] = 00:15, ..., [94] = 23:45
    probability = models.ArrayField(model_container=Probability)

class Garage(models.Model):
    # name of the parking garage/structure/lot. Cannot be None/NULL/Empty String
    name = models.CharField(max_length=50, null=False, blank=False)
    # start of the enforcement period. Cannot be None/NULL
    start_enforce_time = models.TimeField(null=False, blank=False)
    # end of the enforcement period. Cannot be None/NULL
    end_enforce_time = models.TimeField(null=False, blank=False)
    # whether the enforcement period applies to weekends. Default is False
    enforced_on_weekends = models.BooleanField(default=False)
    # array/list of DayProbability. [0] = Sunday, ..., [6] = Saturday
    probability = models.ArrayField(model_container=DayProbability)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

class Ticket(models.Model):
    # dateTime of the ticket. Cannot be None/NULL
    date = models.DateTimeField(null=False, blank=False)
    # garage/location of the ticket. Cannot be None/NULL
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, null=False, blank=False)
    # user who submitted the ticket. Should only be None/NULL for test data
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, default=None)

    def day_of_week(self):
        return self.date.strftime('%a')

    day_of_week.short_description = 'Day Of Week'

class Park(models.Model):
    # start dateTime. Cannot be None/NULL
    start = models.DateTimeField(null=False, blank=False)
    # end dateTime. None/NULL if ongoing
    end = models.DateTimeField(default=None)
    # ticket reference. Not ticketed for that park if set to None/NULL
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, default=None, null=True)
    # garage/location of the park. Cannot be None/NULL
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, null=False, blank=False)

class User(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    park = models.ArrayField(model_container=Park)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def __str__(self):
        return self.email
