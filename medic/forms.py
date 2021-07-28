from django import forms

from django.core.exceptions import ValidationError
import re # for regular expression

from .models import *

class CreateOrUpdateHospitalForm(forms.ModelForm):
	name = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Hospital Name"}))
	phone_number = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Phone Number"}), max_length=Hospital._meta.get_field('phone_number').max_length)
	address = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Address"}), max_length=Hospital._meta.get_field('address').max_length)
	city = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"City"}), max_length=Hospital._meta.get_field('city').max_length)
	district = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"District"}), max_length=Hospital._meta.get_field('district').max_length)

	name_in_google_maps = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Hospital Name in Google Maps"}), required=False)

	image = forms.ImageField(label='Image',widget=forms.FileInput,required=False)

	additional_info = forms.CharField(label='(Optional) Additional Info', widget=forms.Textarea(attrs={'placeholder':"Write any additional information here. For example: You can write additional contact details here."}), required=False)

	# manager_doctor==something , when create. manager_doctor==none , when update
	def save(self, manager_doctor=None, commit=True):
		instance = super().save(commit=True)

		if manager_doctor:
			instance.managers.add(manager_doctor)
			instance.doctors.add(manager_doctor)

		if commit:
			instance.save()
		
		return instance

	def clean(self):
		form_data_cleaned = self.cleaned_data
		valid_phone_regex = r"^[+]([0-9]{13})$|^([0-9][0-9][0-9]+)$" # +880... or 01.... or special hotline numbers like 333 for example

		if not re.search( valid_phone_regex , form_data_cleaned.get('phone_number') ):
			raise ValidationError("Please enter a valid Phone Number")

		return form_data_cleaned
		

	class Meta:
		model = Hospital
		fields = ['name','phone_number','address','city','district', 'name_in_google_maps', 'image', 'additional_info']


class DoctorScheduleForm(forms.ModelForm):
	YEARS = [x for x in range(2020,2031)]
	
	# fields 	
	start_date = forms.DateField(label="Start Date", widget=forms.SelectDateWidget(years=YEARS,attrs={'class':'space_below'}))
	start_time = forms.TimeField(label="Start Time", widget=forms.TextInput(attrs={'class':'input_bottom_outline', 'placeholder':"Example: 21:30"}) )
	end_time = forms.TimeField(label="End Time", widget=forms.TextInput(attrs={'class':'input_bottom_outline', 'placeholder':"Example: 23:30"}) )
	fee = forms.IntegerField(label="Fee", widget=forms.NumberInput(attrs={'class':'input_bottom_outline', 'placeholder':"Example: 500", 'min':'0',}))
	total_available_slot = forms.IntegerField(label="Total Slot", widget=forms.NumberInput(attrs={'class':'input_bottom_outline', 'placeholder':'Example: 40', 'min':'1'}))

	# methods
	def clean(self):
		super().clean()
    
		if self.cleaned_data['start_time'] > self.cleaned_data['end_time']:
			error_message = 'Start time can not be smaller than End time'
			self.add_error('end_time', error_message)
			self.add_error('start_time', error_message)

			# check for slot change and capacity

			return self.cleaned_data


	def save(self, doctor=None, chember_id=None, commit=True):
		instance = super().save(commit=False)

		if chember_id:
			instance.chember_id = chember_id

		if 'start_time' in self.changed_data or 'start_time' in self.changed_data :
			instance.rescheduled = True
			# send notifications when needed

		if doctor:
			instance.doctor = doctor

		if commit:
			instance.save()
		
		return instance

	class Meta:
		model = DoctorsSchedule
		fields = ['start_date', 'start_time', 'end_time', 'fee', 'total_available_slot']