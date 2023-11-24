import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db import models


class MyUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(
            email,
            password=password,
            **extra_fields
        )


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    last_login = None
    is_active = None
    is_superuser = None
    is_staff = None
    date_joined = None

    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4())
    fullname = models.CharField(max_length=200)
    muid = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=200, unique=True)
    phone = models.CharField(unique=True, max_length=15)
    qr_code = models.CharField(unique=True, max_length=36, default=uuid.uuid4())
    group = models.ForeignKey("Group", on_delete=models.CASCADE, related_name='user_group', null=True)
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    image = models.CharField(max_length=200, null=True)
    game_over_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_permenent = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = MyUserManager()

    @classmethod
    def email_exists(cls, email):
        """
        Check if an email address exists in the User model.
        """

        return cls.objects.filter(email=email).exists()

    class Meta:
        db_table = 'user'


class Group(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4())
    title = models.CharField(max_length=100)
    group_order = models.IntegerField()
    member_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'group'


class ScanLog(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4())
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scan_log_user1', null=True)
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scan_log_user2', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scan_log'


class SystemSettings(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4())
    key = models.CharField(max_length=50, null=True)
    value = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = 'system_settings'



class Treasures(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4())
    title = models.CharField(max_length=50)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='treasures_winner', null=True)
    is_claimed = models.BooleanField(default=False)

    class Meta:
        db_table = 'treasures'


class TreasureLog(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4())
    treasure = models.ForeignKey(Treasures, on_delete=models.CASCADE, related_name='treasure_log_treasure')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='treasure_log_user')
    is_claimed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'treasure_log'
