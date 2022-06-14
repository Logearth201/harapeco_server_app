from django.contrib import admin
from .models import User, AttributeGroupInfo, Group, MailInformation
admin.site.register(User)
admin.site.register(Group)
admin.site.register(AttributeGroupInfo)
admin.site.register(MailInformation)
