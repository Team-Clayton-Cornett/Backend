from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Probability, DayProbability, Garage, Ticket, Park, User
from .forms import UserCreationForm, UserChangeForm

# Register your models here.
@admin.register(Garage)
class GarageAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_enforce_time', 'end_enforce_time', 'enforced_on_weekends', 'latitude', 'longitude',)
    ordering = ('name', 'pk',)
    search_fields = ('name',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('date', 'get_day_of_week', 'garage',)
    ordering = ('date', 'pk',)
    search_fields = ('date', 'get_day_of_week', 'garage',)

@admin.register(Park)
class ParkAdmin(admin.ModelAdmin):
    list_display = ('start', 'end', 'ticket',)
    ordering = ('start', 'end',)
    search_fields = ('start', 'end',)

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('email', 'first_name', 'last_name', 'phone', 'is_superuser', 'is_staff', 'is_active',)
    list_filter = ('is_superuser', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'password', 'phone')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_superuser', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'phone', 'first_name', 'last_name',)
    ordering = ('email', 'first_name', 'last_name',)
