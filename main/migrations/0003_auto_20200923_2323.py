# Generated by Django 3.0.7 on 2020-09-23 17:23

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0002_notifications'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Notifications',
            new_name='Notification',
        ),
    ]
