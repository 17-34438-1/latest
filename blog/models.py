from django.db import models

from user.models import DoctorProfile

# Custom models here
class Post(models.Model):
	author = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
	title=models.CharField(max_length=100,null=False)
	subtitle=models.CharField(max_length=100,null=False,verbose_name="Subtitle", default='', blank=True)
	description = models.TextField(null=False, blank=False, verbose_name="Description")

	featured_image = models.ImageField(upload_to='blog', blank=True, null=True)

	date_created = models.DateTimeField(verbose_name='Posted on', auto_now_add=True)
	last_edit	= models.DateTimeField(verbose_name='Last Edit', auto_now=True)

	def __str__(self):
		return f'{self.title} - by {self.author}'

