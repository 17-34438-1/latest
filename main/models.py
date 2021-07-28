from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from user.models import User, DoctorProfile, DocAsstProfile

# Custom made models
class DoctorAsstReq(models.Model):
	doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, verbose_name="Doctor")
	asst = models.ForeignKey(DocAsstProfile, on_delete=models.CASCADE, verbose_name="Assistant")
	additional_info = models.TextField(verbose_name="Additional Info", default=None, null=True, blank=True)
	create_date_time = models.DateTimeField(verbose_name='On', auto_now_add=True)

	def __str__(self):
		return f'{self.asst} requested to join {self.doctor}'



class Coupon(models.Model):
    coupon_code = models.CharField(max_length=32, unique=True)
    created_by = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, verbose_name="Created by")
    active = models.BooleanField(default=True)
    discount_percent = models.IntegerField(verbose_name="Total Discount Percent (1-100)", validators=[MaxValueValidator(100),MinValueValidator(1)])



class Notification(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	description=models.CharField(max_length=250)
	link=models.TextField(verbose_name="Link")
	seen = models.BooleanField(null=True, verbose_name="Seen", default=False)
	date_created = models.DateTimeField(verbose_name='Posted on', auto_now_add=True)
