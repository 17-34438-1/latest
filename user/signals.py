# was not working from here
# added in the models.py file instead

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import User, UserProfile

# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
# 	print('---------------------------------------------------------------- in CREATE profile signal ---------------------------------------------------------')
# 	if created:
# 		UserProfile.objects.create(user=instance)

# @receiver(post_save, sender=User):
# def save_profile(sender, instance, **kwargs):
# 	print('---------------------------------------------------------------- in SAVE profile signal ---------------------------------------------------------')
# 	instance.userprofile.save()