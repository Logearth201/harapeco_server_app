from django.contrib import admin
from .models import UserComment, GroupTopic, GroupTopicComment, GroupTopicComment
admin.site.register(UserComment)
admin.site.register(GroupTopic)
admin.site.register(GroupTopicComment)