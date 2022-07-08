from email.policy import default
from django.db import models
from app.models import BaseManager
from django.utils import timezone

# Create your models here.
class Platform(models.Model):
    objects = BaseManager()
    platform_name = models.CharField(max_length=100)

    def __str__(self):
        return self.platform_name

class DiamondCount(models.Model):
    user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="DiamondCount_user")
    platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, related_name="DiamondCount_platform", null=True)
    count = models.BigIntegerField()

    def __str__(self):
        return self.user.username + ':' + self.platform.platform_name + " = " + str(self.count)
        
class ExpenseHistory(models.Model):
    objects = BaseManager()
    user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="ExpenseHistory_user")
    platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, related_name="ExpenseHistory_platform", null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    buy_diamonds = models.BigIntegerField()
    date_submited = models.DateTimeField("date_submited", default=timezone.now)

class BuyMenu(models.Model):
    objects = BaseManager()
    platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, related_name="BuyMenu_platform", null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    diamonds = models.BigIntegerField()
