from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from birkoss.models import TimeStampedModel, UUIDModel

from .managers import UserManager


class User(PermissionsMixin, UUIDModel, TimeStampedModel, AbstractBaseUser):
    email = models.EmailField(
        verbose_name='Email Address',
        max_length=255,
        unique=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    firstname = models.CharField(max_length=100, default='')
    lastname = models.CharField(max_length=100, default='')

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.email
