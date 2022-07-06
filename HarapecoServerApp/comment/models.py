from email.policy import default
from django.db import models
from django.utils import timezone
from app.models import BaseManager

# Create your models here.
class UserComment(models.Model):
    objects = BaseManager()
    text = models.TextField(max_length=5000)
    user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="UserComment_user")
    submit_user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="UserComment_submit_user", null=True) # cannot null
    good_cnt = models.IntegerField(default=0)
    bad_cnt = models.IntegerField(default=0)
    is_delete = models.BooleanField(default=False)
    date_submited = models.DateTimeField("date_submited", default=timezone.now)
    date_edited = models.DateTimeField("date_edited", default=timezone.now)

    def __str__(self):
        return self.user.username + '<=' + self.submit_user.username + ":" + self.text[0:20]

class UserCommentEvaluate(models.Model):
    objects = BaseManager()
    user_comment = models.ForeignKey(UserComment, on_delete=models.CASCADE, related_name="UserCommentEvaluate_userComment")
    is_good = models.BooleanField()
    user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="UserCommentEvaluate_user")

    constraints = [
        models.UniqueConstraint(
            fields=["user_comment", "user"],
            name="user_comment_user_unique"
            )
        ]

class GroupTopic(models.Model):
    objects = BaseManager()
    topic_name = models.CharField(max_length=100)
    group = models.ForeignKey("app.Group", on_delete=models.CASCADE)
    is_delete = models.BooleanField(default=False)
    is_not_belong_viewable = models.BooleanField(default=False)

class GroupTopicComment(models.Model):
    objects = BaseManager()
    topic = models.ForeignKey(GroupTopic, on_delete=models.CASCADE, related_name="GroupTopicComment_topic")
    fromuser = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="GroupTopicComment_fromuser")
    text = models.TextField(max_length=5000)
    good_cnt = models.IntegerField(default=0)
    bad_cnt = models.IntegerField(default=0)
    is_delete = models.BooleanField(default=False)
    is_edit = models.BooleanField(default=False)
    date_submited = models.DateTimeField("date_submited", default=timezone.now)
    date_edited = models.DateTimeField("date_edited", default=timezone.now)

class GroupTopicCommentEvaluate(models.Model):
    objects = BaseManager()
    group_topic_comment = models.ForeignKey(GroupTopicComment, on_delete=models.CASCADE, related_name="GroupTopicCommentEvaluate_groupTopicComment")
    is_good = models.BooleanField()
    user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="GroupTopicCommentEvaluate_user")

    constraints = [
        models.UniqueConstraint(
            fields=["group_topic_comment", "user"],
            name="group_topic_comment_user_unique"
            )
        ]
