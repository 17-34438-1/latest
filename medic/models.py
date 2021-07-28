from django.db import models

from django.urls import reverse

from user.models import *
from main.models import Notification

# Create your models here.
class Hospital(models.Model):
	name = models.CharField(verbose_name="Hospital Name", max_length=60)
	phone_number = models.CharField(verbose_name="Phone Number", max_length=14)

	image = models.ImageField(default='no_image.jpg', upload_to='hospitals')

	address = models.CharField(verbose_name="Address", max_length=60)
	city = models.CharField(verbose_name="City", max_length=60)
	district = models.CharField(verbose_name="District", max_length=60)
	additional_info = models.TextField(verbose_name="Additional Info", default="", blank=True)
	name_in_google_maps = models.CharField(verbose_name="Name in Google Map", max_length=128, blank=True, null=True)	
	
	managers =  models.ManyToManyField(DoctorProfile, related_name='manages', verbose_name="Manager Doctor(s)")

	doctors = models.ManyToManyField(DoctorProfile, verbose_name="Doctor(s) available in this hospital")

	active = models.BooleanField(verbose_name="Active (Y/N)", default=True)

	def __str__(self):
		return f'Hospital {self.name}'




class DoctorsSchedule(models.Model):
	doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, verbose_name="Doctor", null=True, blank=True)
	start_date = models.DateField(verbose_name="Start Date", null=True, blank=True)
	start_time = models.TimeField(verbose_name="Start Time", null=True, blank=True)
	end_time = models.TimeField(verbose_name="End Time", null=True, blank=True)
	fee = models.IntegerField(verbose_name="Fee", default=0, null=True, blank=True)
	total_available_slot = models.IntegerField(verbose_name="Total Available Slots", null=True, blank=True)
	booked_slot = models.IntegerField(verbose_name="Total Booked Slots", default=0, null=True, blank=True)

	chember = models.ForeignKey(Hospital, on_delete=models.CASCADE)

	rescheduled = models.BooleanField(verbose_name="Rescheduled (Y/N)", default=False)
	rescheduled_on = models.DateTimeField(verbose_name='Rescheduled on', null=True, auto_now=True)

	def __str__(self):
		return f'Schedule #{self.id} of {self.doctor.user.username}'

	def slot_available(self):
		return (self.total_available_slot - self.booked_slot) > 0

	def remaining_seat(self):
		return self.total_available_slot - self.booked_slot



class Appointment(models.Model):
	schedule = models.ForeignKey(DoctorsSchedule, on_delete=models.CASCADE, verbose_name="Schedule")
	patient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Patient")
	ref_by = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, verbose_name="Referenced By", null=True, default=None, blank=True)
	issue_title = models.CharField(verbose_name="Issue Title", max_length=60)
	issue_desc = models.TextField(verbose_name="Issue Description", default="", blank=True)
	#status = models.CharField(verbose_name="Status", max_length=48, default="Awaiting Confirmation")

	STATUS_AWAITING_CONFIRMATION = 0
	STATUS_AWAITING_PAYMENT = 1
	STATUS_CONFIRMED = 2
	STATUS_CANCELLED = 3
	STATUS_CHOICES = [
		(STATUS_AWAITING_CONFIRMATION, "Awaiting Confirmation"),
		(STATUS_AWAITING_PAYMENT, 'Waiting for Payment'), 
		(STATUS_CONFIRMED, 'Confirmed'),
		(STATUS_CANCELLED, 'Cancelled'),
	]
	status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_AWAITING_CONFIRMATION)
	
	#reschedule configs - for future

	#prescription related config - for future



	def __str__(self):
		return f'#{self.id} - Patient {self.patient} , {self.schedule.doctor}'







##################### SIGNALS #########################
@receiver(post_save, sender=Appointment)
def create_notification(sender, instance, **kwargs):
	if instance.status == Appointment.STATUS_AWAITING_CONFIRMATION : 
		instance.schedule.booked_slot = instance.schedule.booked_slot + 1
		instance.schedule.save()

	if instance.status == Appointment.STATUS_AWAITING_PAYMENT : 
		notification = Notification(
			user=instance.patient,
			description=f'Your appointment (#{instance.id}) has been approved. Please pay to confirm your booking.',
			link= f'/appointment/{instance.id}'
		)
		notification.save()