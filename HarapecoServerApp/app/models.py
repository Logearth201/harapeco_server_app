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

class AttributeGroupInfo(models.Model):
    objects = BaseManager()
    user = models.ForeignKey("app.User", on_delete=models.CASCADE)
    group = models.ForeignKey("app.Group", on_delete=models.CASCADE)
    authentication = models.IntegerField(default=1) # 0：リーダー、1：一般ユーザー
    group_join_waitconfirm = models.BooleanField(default=False)

class UserComment(models.Model):
    objects = BaseManager()
    content = models.CharField(max_length=5000)
    like_count = models.IntegerField(default=0)
    dislike_count = models.IntegerField(default=0)
    is_delete = models.BooleanField(default=False)
    user = models.ForeignKey("app.User", on_delete=models.CASCADE)
