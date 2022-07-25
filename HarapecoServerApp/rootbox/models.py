from itertools import permutations
from django.db import models
from app.models import User

# Create your models here.
class RootBoxTerm(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=4000)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    common_prefix_key = models.CharField(max_length=100)

class RootBoxItem(models.Model):
    term = models.ForeignKey(RootBoxTerm, on_delete=models.CASCADE)
    event = models.CharField(max_length=500)
    permutation = models.IntegerField()

class UserRootBoxState(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="UserRootBoxState_user")
    term = models.ForeignKey(RootBoxTerm, on_delete=models.CASCADE, related_name="UserRootBoxState_term")
    hash_key_usr = models.CharField(max_length=100)
    hash_key_index = models.CharField(max_length=100)
