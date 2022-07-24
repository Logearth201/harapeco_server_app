from django.db import models
from app.models import User

# Create your models here.
class ElectionTitle(models.Model):
    name = models.CharField(max_length=100)

class ElectionUnit(models.Model):
    name = models.CharField(max_length=100)
    election_title = models.ForeignKey(ElectionTitle, on_delete=models.CASCADE)
    election_start_time = models.DateTimeField()
    election_end_time = models.DateTimeField()

class ElectionCandidate(models.Model):
    name = models.CharField(max_length=100)
    election_unit = models.ForeignKey(ElectionUnit, on_delete=models.CASCADE, related_name="ElectionCandidate_election_unit")

class ElectionUserSubmit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    election_unit = models.ForeignKey(ElectionUnit, on_delete=models.CASCADE, related_name="ElectionUserSubmit_election_unit")
    election_candidate = models.ForeignKey(ElectionCandidate, on_delete=models.SET_NULL, null=True, related_name="ElectionUserSubmit_election_candidate")
