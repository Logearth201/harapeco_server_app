from django.contrib import admin
from .models import ElectionTitle, ElectionUnit, ElectionCandidate, ElectionUserSubmit
admin.site.register(ElectionTitle)
admin.site.register(ElectionUnit)
admin.site.register(ElectionCandidate)
admin.site.register(ElectionUserSubmit)
