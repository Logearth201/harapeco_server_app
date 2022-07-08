from email.policy import default
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.mail import send_mail
from django.utils import timezone

class BaseManager(models.Manager):
    def get_or_none(self, **kwargs):
        """
        検索にヒットすればそのモデルを、しなければNoneを返します。
        """
        try:
            return self.get_queryset().get(**kwargs)
        except self.model.DoesNotExist:
            return None

class UserManager(BaseUserManager):
    """カスタムユーザーマネージャーモデル"""
    use_in_migrations = True

    def get_or_none(self, **kwargs):
        """
        検索にヒットすればそのモデルを、しなければNoneを返します。
        """
        try:
            return self.get_queryset().get(**kwargs)
        except self.model.DoesNotExist:
            return None

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self._create_user(username, "test@testmail.com", password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル"""
    username = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=100, unique=True)
    #フォロイーフィールドをUser自身に持たせる
    followees = models.ManyToManyField('self', blank=True, symmetrical=False)
    is_staff = models.BooleanField("is_staff", default=False)
    is_active = models.BooleanField("is_active", default=True)
    date_joined = models.DateTimeField("date_joined", default=timezone.now)
    
    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

class Group(models.Model):
    objects = BaseManager()
    name = models.CharField(max_length=100)
    explain = models.CharField(max_length=100)
    score = models.IntegerField(default=0)
    is_delete = models.BooleanField(default=False)
    auto_belong_group = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class AttributeGroupInfo(models.Model):
    objects = BaseManager()
    user = models.ForeignKey("app.User", on_delete=models.CASCADE)
    group = models.ForeignKey("app.Group", on_delete=models.CASCADE)
    authentication = models.IntegerField(default=1) # 0：リーダー、1：一般ユーザー
    group_join_waitconfirm = models.BooleanField(default=False)

    def __str__(self):
        return "User = " + self.user.username + ', Group = ' + self.group.name + " as " + str(self.authentication)

class MailInformation(models.Model):
    objects = BaseManager()
    email = models.EmailField(max_length=70)
    hash_address = models.CharField(max_length=100)
    valid_time = models.TimeField()
    username = models.CharField(max_length=100)
    tmp_password = models.CharField(max_length=50)

class UserDeviceLogin(models.Model):
    objects = BaseManager()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    auth_key = models.CharField(max_length=200,default="",db_index=True)
    push_notification_token = models.CharField(max_length=100)
    register_datetime = models.DateTimeField(default=timezone.now)

# 各種重要な手続きデータを保存するためのモデル。ログインは除く。
class ProcessSaver(models.Model):
    objects = BaseManager()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    valid_time = models.TimeField()
    process_type = models.CharField(max_length=15)
    data = models.CharField(max_length=4000)
    password = models.CharField(max_length=100)

# 招待コード
class Invitation(models.Model):
    objects = BaseManager()
    inviter_user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    invite_token = models.CharField(max_length=100)
    is_valid = models.BooleanField(default=True)
    date_add = models.DateTimeField("date_joined", default=timezone.now)

    indexes = [
        models.Index(fields=['is_valid', 'date_add']),
    ]