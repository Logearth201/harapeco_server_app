from email.policy import default
from django.db import models
from app.models import User, BaseManager

# Create your models here.
class ElectionTitle(models.Model):
    name = models.CharField(max_length=100)
    is_delete = models.BooleanField(default=False)

class ElectionUnit(models.Model):
    objects = BaseManager()
    name = models.CharField(max_length=100)
    election_title = models.ForeignKey(ElectionTitle, on_delete=models.CASCADE)
    election_start_time = models.DateTimeField()
    election_end_time = models.DateTimeField()

class ElectionCandidate(models.Model):
    objects = BaseManager()
    name = models.CharField(max_length=100)
    election_unit = models.ForeignKey(ElectionUnit, on_delete=models.CASCADE, related_name="ElectionCandidate_election_unit")
    final_get_submits = models.BigIntegerField(default=0) # at last, this record can be counted election votes.

class ElectionUserSubmit(models.Model):
    objects = BaseManager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    election_unit = models.ForeignKey(ElectionUnit, on_delete=models.CASCADE, related_name="ElectionUserSubmit_election_unit")
    election_candidate = models.ForeignKey(ElectionCandidate, on_delete=models.SET_NULL, null=True, blank=True, related_name="ElectionUserSubmit_election_candidate")

    def save(self, *args, **kwargs):
         if not self.election_candidate:
              self.election_candidate = None
         super(ElectionUserSubmit, self).save(*args, **kwargs)
