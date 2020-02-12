from django.contrib import admin
from .models import Probability, DayProbability, Garage, Ticket, Park

# Register your models here.
@admin.register(Garage)
class GarageAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_enforce_time', 'end_enforce_time', 'enforced_on_weekends', 'latitude', 'longitude',)
    ordering = ('name', 'pk',)
    search_fields = ('name',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('date', 'get_day_of_week', 'garage', 'user',)
    ordering = ('date', 'pk',)
    search_fields = ('date', 'get_day_of_week', 'garage',)

@admin.register(Park)
class ParkAdmin(admin.ModelAdmin):
    list_display = ('start', 'end', 'user', 'ticket',)
    ordering = ('start', 'end', 'user',)
    search_fields = ('start', 'end', 'user',)
