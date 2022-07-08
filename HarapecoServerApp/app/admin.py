from django.contrib import admin
from .models import User, AttributeGroupInfo, Group, MailInformation, ProcessSaver, UserDeviceLogin, Invitation
admin.site.register(User)
admin.site.register(Group)
admin.site.register(AttributeGroupInfo)
admin.site.register(MailInformation)
admin.site.register(UserDeviceLogin)
admin.site.register(ProcessSaver)
admin.site.register(Invitation)
