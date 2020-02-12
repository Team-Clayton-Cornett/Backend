from djongo import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

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
    # day of week enumeration. see DayOfWeekEnum above for values
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    # garage/location of the ticket. Cannot be None/NULL
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, null=False, blank=False)
    # user who was ticketed. If None/NULL, the ticket was not reported by a specific user.
    # *this should only be None/NULL for test data*
    user = models.ForeignKey(User, on_delete=models.SET_NULL, default=None, null=True)

    def get_day_of_week(self):
        return self.get_day_of_week_display()

    get_day_of_week.short_description = 'Day Of Week'

class Park(models.Model):
    # start dateTime. Cannot be None/NULL
    start = models.DateTimeField(null=False, blank=False)
    # end dateTime. None/NULL if ongoing
    end = models.DateTimeField(default=None)
    # user that created the park entry. Cannot be None/NULL
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    # ticket reference. Not ticketed for that park if set to None/NULL
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, default=None, null=True)
