from django.contrib import admin
from .models import Probability, DayProbability, Garage, Ticket, Park

# Register your models here.
admin.site.register(Garage)
admin.site.register(Ticket)
admin.site.register(Park)