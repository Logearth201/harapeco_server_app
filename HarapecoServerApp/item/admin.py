from django.contrib import admin
from .models import Stamp, Platform, DiamondCount, ExpenseHistory
admin.site.register(Stamp)
admin.site.register(Platform)
admin.site.register(DiamondCount)
admin.site.register(ExpenseHistory)