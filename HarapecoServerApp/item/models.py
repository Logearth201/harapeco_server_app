from email.policy import default
from django.db import models
from app.models import BaseManager
from django.utils import timezone

# all user common item.
class Stamp(models.Model):
    objects = BaseManager()
    stamp_name = models.CharField(max_length=100)
    stamp_filename = models.CharField(max_length=100)

