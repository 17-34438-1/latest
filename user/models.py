from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.db.models.signals import post_save
from django.dispatch import receiver

from PIL import Image

# Create your models here.
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/
# https://www.youtube.com/watch?v=HshbjK1vDtY

class UserAccountManager(BaseUserManager):
	def create_user(self, username, email, password=None):
		if not username:
			raise ValueError('Username is required')
		if not email: 
			raise ValueError('Email is required')

		user = self.model(
			email=self.normalize_email(email),
			username=username
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, username, email, password):
		user = self.create_user(
			username=username,
			email=self.normalize_email(email),
			password=password,
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user

	def get_by_natural_key(self, username):
		return self.get(username__iexact=username)




class User(AbstractBaseUser):
	# FIELDS 
	# implenting required ones 
	email 		= models.EmailField(verbose_name='Email', max_length=60, unique=True)
	username	= models.CharField(verbose_name='Username',max_length=30, unique=True) 
	# auto filled fields
	date_joined = models.DateTimeField(verbose_name='Join Date', auto_now_add=True)
	last_login	= models.DateTimeField(verbose_name='Last Login', auto_now=True)
	is_admin	= models.BooleanField(default=False)
	is_active	= models.BooleanField(default=True)
	is_staff	= models.BooleanField(default=False)
	is_superuser= models.BooleanField(default=False)

	# Custom Fields
	first_name	= models.CharField(verbose_name='First Name', max_length=30, unique=False, default='') 
	last_name	= models.CharField(verbose_name='Last Name', max_length=30, unique=False, default='') 
	dob 		= models.DateField(verbose_name='Date of Birth', null=True)

	# Not so efficient way, but lets keep it for now (not having address in a diff model)
	address = models.CharField(verbose_name='Address', max_length=50, unique=False, default='', null=True, blank=True) 
	city = models.CharField(verbose_name='Town/City', max_length=30, unique=False, default='', null=True, blank=True) 
	district = models.CharField(verbose_name='District', max_length=30, unique=False, default='', null=True, blank=True) 
	
	# Default unavailable
	UNAVAILABLE = '-'

	# Gender
	GENDER_MALE = 'M'
	GENDER_FEMALE = 'F'
	GENDER_CHOICES = [
		(UNAVAILABLE, "Unavailable"),
		(GENDER_MALE, 'Male'), 
		(GENDER_FEMALE, 'Female')
	]
	gender = models.CharField(choices=GENDER_CHOICES, max_length=1, default=UNAVAILABLE)

	# Blood Group
	BLOOD_GROUP_CHOICES = [
		(UNAVAILABLE,"Unavailable"),
		("A+","A+"), 
		("A-","A-"),
		("B+","B+"),
		("B-","B-"),
		("O+","O+"),
		("O-","O-"),
		("AB+","AB+"),
		("AB-","AB-"),
	]
	blood_group = models.CharField(choices=BLOOD_GROUP_CHOICES, max_length=3, default=UNAVAILABLE)


	# User Type : we have the following type for now : Patient , Doctor, DoctorsAssisstant
	USER_TYPE_PATIENT = 'P'
	USER_TYPE_DOC = 'D'
	USER_TYPE_DOC_ASST = 'DA'
	USER_TYPE_CHOICES = [
		(USER_TYPE_PATIENT, 'Patient'), 
		(USER_TYPE_DOC, 'Doctor'),
		(USER_TYPE_DOC_ASST, "Doctor's Assistant")
	]

	user_type = models.CharField(choices=USER_TYPE_CHOICES , max_length=2)


	
	# CONFIG
	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['email', ]

	objects = UserAccountManager()


	def __str__(self):
		return self.username

	# implementing the abstract methods
	def has_perm(self, perm, obj=None):
		return self.is_admin

	def has_module_perms(self, app_label):
		return True

	def save(self, *args, **kwargs):
		self.username = self.username.lower()
		return super(User, self).save(*args, **kwargs)

	def fullname(self):
		return f'{self.first_name} {self.last_name}'





# PROFILES
class PatientProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	image = models.ImageField(default='default.jpg', upload_to='patient_profile_pics')
	
	height_cm = models.IntegerField(null=True, verbose_name="Height (cm)", default=None, blank=True)
	weight_kg = models.IntegerField(null=True, verbose_name="Weight (kg)", default=None, blank=True)
	bloodPressure = models.BooleanField(null=True, verbose_name="Blood Pressure", default=None, blank=True)
	diabetes = models.BooleanField(null=True, verbose_name="Diabetes", default=None, blank=True)

	last_update	= models.DateTimeField(verbose_name='Last Updated', auto_now=True)

	def __str__(self):
		return f'Patient {self.user.username}'

	def save(self, *args, **kwargs):
		super().save()

		img = Image.open(self.image.path)
		img_max_size = 500

		if img.height > img_max_size or img.width > img_max_size:
			img.thumbnail((img_max_size,img_max_size))
			img.save(self.image.path)




class DoctorProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	image = models.ImageField(default='default.jpg', upload_to='doctor_profile_pics')
	
	review_rating = models.FloatField(verbose_name="Rating", default=0.0)
	total_review = models.IntegerField(verbose_name="Number of Reviews", default=0)
	bio_desc = models.TextField(verbose_name="Doctor Bio", default='No information available')
	specialist = models.BooleanField(null=True, verbose_name="Specialist",)
	education = models.CharField(verbose_name='Education', max_length=250, default='N/A') 
	exp_years = models.IntegerField(verbose_name="Experience (years)", default=0)
	total_num_of_chember = models.IntegerField(verbose_name="Total number of Chembers", default=0)
	field = models.CharField(verbose_name='Field of Expertise', max_length=100, default='N/A')
	approx_fee_range_high = models.IntegerField(verbose_name="Approx. Fee Range (Highest)", default=0)
	approx_fee_range_low = models.IntegerField(verbose_name="Approx. Fee Range (Lowest)", default=0)

	#main_chember = models.CharField(verbose_name='Main Chember', max_length=150, default='Unknown')

	apprived = models.BooleanField(verbose_name="Approved", default=False)
	#maybe we can put a "approved by" field later if needed.

	last_update	= models.DateTimeField(verbose_name='Last Updated', auto_now=True)

	# search tags
	seach_tags = models.TextField(verbose_name="Search Tags", blank=True, null=True, default=None)

	def __str__(self):
		return f'Doctor {self.user.username}'

	# def get_doctor_hospital_list_for_dropdown(self):
	# 	hospitals = self.hospital_set.all()
	# 	hospital_for_dropdown = [tuple([x,x]) for x in hospitals]

	# 	return hospital_for_dropdown

	def save(self, *args, **kwargs):
		super().save()

		img = Image.open(self.image.path)
		img_max_size = 500

		if img.height > img_max_size or img.width > img_max_size:
			img.thumbnail((img_max_size,img_max_size))
			img.save(self.image.path)





class DocAsstProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE) 
	image = models.ImageField(default='default.jpg', upload_to='docasst_profile_pics')
	
	doctor = models.ForeignKey(DoctorProfile, blank=True, null=True, default=None, on_delete=models.SET_NULL)

	def __str__(self):
		return f'Doctor\'s Asst. {self.user.username}'

	def save(self, *args, **kwargs):
		super().save()

		img = Image.open(self.image.path)
		img_max_size = 500

		if img.height > img_max_size or img.width > img_max_size:
			img.thumbnail((img_max_size,img_max_size))
			img.save(self.image.path)



# temp doctor profile info (added by docasst, needs approval)
# code here (copy paste - doctor : foreign key)





##################### SIGNALS #########################
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
	if created:
		if instance.user_type == User.USER_TYPE_PATIENT:
			PatientProfile.objects.create(user=instance)
		if instance.user_type == User.USER_TYPE_DOC:
			DoctorProfile.objects.create(user=instance)
		if instance.user_type == User.USER_TYPE_DOC_ASST:
			DocAsstProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
	if instance.user_type == User.USER_TYPE_PATIENT:
		instance.patientprofile.save()
	if instance.user_type == User.USER_TYPE_DOC:
		instance.doctorprofile.save()
	if instance.user_type == User.USER_TYPE_DOC_ASST:
		instance.docasstprofile.save()
