from django.contrib import admin
from .models import *

# Customnization
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('__str__','status',)

# Register your models here.
admin.site.register(DoctorsSchedule)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Hospital)