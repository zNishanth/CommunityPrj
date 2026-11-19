from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, username, name=None, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            name=name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, name=None, password=None):
        user = self.create_user(email=email, username=username, name=name, password=password)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="Email address", max_length=255, unique=True)
    username = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.username

    @property
    def is_staff(self):
        return self.is_superuser


class ReportedURL(models.Model):
    url = models.URLField(max_length=2048)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    reported_date = models.DateTimeField(default=timezone.now)
    confirmed = models.BooleanField(default=False)
    chain_tx_hash = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self) -> str:
        user_label = self.user.username if self.user else "auto-flagged"
        return f"{self.url} by {user_label}"
