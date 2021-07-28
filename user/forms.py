from django import forms
#from django.contrib.auth.models import User
#from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import *

class UserCreationForm(forms.ModelForm):
	YEARS = [x for x in range(1920,2020)]

	"""A form for creating new users. Includes all the required
	fields, plus a repeated password."""
	password1 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Password"}))
	password2 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Confirm Password"}))

	#custom
	username = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Usernamae"}))
	first_name = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'input_bottom_outline firstName', 'placeholder':"First Name"}))
	last_name = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'input_bottom_outline lastName', 'placeholder':"Last Name"}))
	email = forms.EmailField(label='', widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Email Address"}))
	dob = forms.DateField(label="Date of Birth", widget=forms.SelectDateWidget(years=YEARS,attrs={'class':'space_below'}))
	gender = forms.CharField(label='Gender' , widget=forms.Select(choices=User.GENDER_CHOICES,))
	blood_group = forms.CharField(label='Blood Group' , widget=forms.Select(choices=User.BLOOD_GROUP_CHOICES))
	user_type = forms.CharField(label='Join as' , widget=forms.Select(choices=User.USER_TYPE_CHOICES))

	# #address
	# address = forms.CharField(label="Address", required=False)
	# city = forms.CharField(label="City", required=False)
	# district = forms.CharField(label="District", required=False)

	class Meta:
		model = User
		# fields = ('email',)
		fields = (
			'first_name',
			'last_name',
			'username',
			'email',
			'password1',
			'password2',
			'dob',
			'gender',
			'blood_group',
			'user_type',
		)

	def clean_email(self):
		email = self.cleaned_data.get('email')
		qs = User.objects.filter(email=email)
		if qs.exists():
			raise forms.ValidationError("Email is taken")
		return email

	def clean_password2(self):
		# Check that the two password entries match
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2

	def save(self, commit=True):
		# Save the provided password in hashed format
		user = super().save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user


class UserChangeForm(forms.ModelForm):
	"""A form for updating users. Includes all the fields on
	the user, but replaces the password field with admin's
	password hash display field.
	"""
	password = ReadOnlyPasswordHashField()

	class Meta:
		model = User
		fields = ('email', 'password', 'dob', 'is_active', 'is_admin')

	def clean_password(self):
		# Regardless of what the user provides, return the initial value.
		# This is done here, rather than on the field, because the
		# field does not have access to the initial value
		return self.initial["password"]





class LoginForm(AuthenticationForm):
	username = forms.CharField(widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Username or Phone or Email"}))
	password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Password"}))



class UserUpdateForm(forms.ModelForm):
	YEARS = [x for x in range(1920,2020)]

	first_name = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'input_bottom_outline firstName', 'placeholder':"First Name"}))
	last_name = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'input_bottom_outline lastName', 'placeholder':"Last Name"}))
	username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Username"}))
	email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Email Address"}))
	dob = forms.DateField(label="Date of Birth", widget=forms.SelectDateWidget(years=YEARS,attrs={'class':'space_below'}))
	gender = forms.CharField(label='Gender' , widget=forms.Select(choices=User.GENDER_CHOICES,))
	blood_group = forms.CharField(label='Blood Group' , widget=forms.Select(choices=User.BLOOD_GROUP_CHOICES))

	#address
	address = forms.CharField(label="Address", required=False, widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Address"}))
	city = forms.CharField(label="City", required=False, widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"City"}))
	district = forms.CharField(label="District", required=False, widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"District"}))

	class Meta:
		model = User
		fields = ['first_name','last_name','username','email','dob','gender','blood_group','address','city','district']


class DoctorProfileUpdate(forms.ModelForm):
	image = forms.ImageField(label='',widget=forms.FileInput(attrs={'class':'hidden'}),required=False)

	field = forms.CharField(label='Field of Expertise', widget=forms.TextInput(attrs={'placeholder':"Field", 'class':'input_bottom_outline full_width'}))
	exp_years = forms.IntegerField(label="Years of Experience", widget=forms.NumberInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Experience (years)", 'min':'0',}))
	specialist = forms.BooleanField(label='Specialist',required=False)

	bio_desc = forms.CharField(label='About Me', widget=forms.Textarea(attrs={'placeholder':"Write your bio..."}))

	#main_chember = forms.CharField(label="Main Chember", widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Main Chember"}))
	total_num_of_chember = forms.IntegerField(label="Total number of Chembers", widget=forms.NumberInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Main Chember", 'min':'1',}))

	education = forms.CharField(label='Education', widget=forms.TextInput(attrs={'placeholder':"Education", 'class':'input_bottom_outline full_width'}))

	approx_fee_range_high = forms.IntegerField(label="Approx. Fee (Highest)", widget=forms.NumberInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Approx. Fee (Highest)", 'min':'0',}))
	approx_fee_range_low = forms.IntegerField(label="Approx. Fee (Lowest)", widget=forms.NumberInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Approx. Fee (Highest)", 'min':'0',}))

	seach_tags = forms.CharField(required=False, label='Search Tag (Optional) (Not visible on your profile, only used for search)', widget=forms.Textarea(attrs={'placeholder':"Write some tags which will help our search system to find your profile. This is only shown to you and not visible to other users. Each tag should be seperated by space. Example: orthopedics bones bone specialist "}))

	class Meta:
		model = DoctorProfile
		fields = ['image','field','exp_years','specialist','bio_desc', 'total_num_of_chember','education','approx_fee_range_high','approx_fee_range_low', 'seach_tags']


class PatientProfileUpdate(forms.ModelForm):
	image = forms.ImageField(label='',widget=forms.FileInput(attrs={'class':'hidden'}),required=False)

	height_cm = forms.IntegerField(label="Height (cm)", widget=forms.NumberInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Height (cm)", 'min':'0',}), required=False)
	weight_kg = forms.IntegerField(label="Weight (kg)", widget=forms.NumberInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Weight (kg)", 'min':'0',}), required=False)

	bloodPressure = forms.NullBooleanField(label='Blood Pressure' , widget=forms.NullBooleanSelect, required=False)
	diabetes = forms.NullBooleanField(label='Diabetes' , widget=forms.NullBooleanSelect, required=False)

	class Meta:
		model = PatientProfile
		fields = ['image','height_cm','weight_kg','bloodPressure','diabetes']


class DocAsstProfileUpdate(forms.ModelForm):
	image = forms.ImageField(label='',widget=forms.FileInput(attrs={'class':'hidden'}),required=False)

	class Meta:
		model = DocAsstProfile
		fields = ['image']