from django.core.management.base import BaseCommand
from app.models import Group, User
from comment.models import UserComment, GroupTopic, GroupTopicComment

# python manage.py cyclicclearで起動、古いデータを捨てる
class Command(BaseCommand):
    def handle(self, *args, **options):
        Group.objects.filter(is_delete=True).delete()
        User.objects.filter(is_active=False).delete()
        UserComment.objects.filter(is_delete=True).delete()
        GroupTopic.objects.filter(is_delete=True).delete()
        GroupTopicComment.objects.filter(is_delete=True).delete()
